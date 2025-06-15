---
layout: default
title: Privacy & Security
parent: Technical Documentation
nav_order: 5
---

# Privacy & Security Architecture
{: .no_toc }

## Table of contents
{: .no_toc .text-delta }

1. TOC
{:toc}

---

## Overview

FeedForward implements a comprehensive security and privacy architecture designed to protect sensitive educational data while enabling effective AI-powered feedback. The system follows privacy-by-design principles and implements defense-in-depth security strategies.

## Privacy Architecture

### Privacy Principles

FeedForward adheres to core privacy principles:

```yaml
Core Principles:
  Data Minimization:
    - Collect only necessary data
    - Automatic content deletion
    - Metadata retention only
    
  Purpose Limitation:
    - Data used only for feedback
    - No training on student data
    - Clear usage boundaries
    
  Transparency:
    - Clear privacy policy
    - Visible data handling
    - User control options
    
  Security:
    - Encryption at rest
    - Encrypted transmission
    - Access controls
```

### Student Submission Privacy

The most sensitive data—student submissions—receives special handling:

```python
class PrivacyFocusedSubmissionHandler:
    async def process_submission(self, draft_id: int):
        """Process submission with privacy safeguards"""
        draft = await self.load_draft(draft_id)
        
        try:
            # Generate feedback
            feedback = await self.generate_feedback(draft.content)
            
            # Store results (not content)
            await self.store_feedback(draft_id, feedback)
            
        finally:
            # Always remove content unless preserved
            if not draft.content_preserved:
                await self.remove_content(draft_id)
                await self.log_removal(draft_id)
    
    async def remove_content(self, draft_id: int):
        """Securely remove submission content"""
        # Overwrite with empty string
        await db.update_draft(
            draft_id,
            content='',
            content_removed_date=datetime.utcnow()
        )
        
        # Force database cleanup
        await db.execute("VACUUM")
```

### Data Lifecycle Management

Clear lifecycle for all data types:

```
Student Submission Lifecycle:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. Submission (Temporary Storage)
   ├── Content encrypted in transit
   ├── Stored temporarily in database
   └── Access limited to student + instructor

2. Processing (Isolated Access)
   ├── AI accesses via secure API
   ├── No permanent storage in AI
   └── Audit log of access

3. Feedback Generation (Result Storage)
   ├── Only feedback stored
   ├── Metadata retained
   └── Original content queued for deletion

4. Content Removal (Automatic)
   ├── Content overwritten
   ├── Database space reclaimed
   └── Removal logged

5. Long-term (Metadata Only)
   ├── Scores and feedback retained
   ├── Progress tracking maintained
   └── No original content
```

### Privacy Controls

User-controllable privacy settings:

```yaml
Student Privacy Controls:
  Submission Visibility:
    - Hide from view (soft delete)
    - Unhide when needed
    - No instructor override
    
  Data Export:
    - Download all personal data
    - Machine-readable format
    - Include all metadata
    
  Account Deletion:
    - Request account removal
    - Grace period provided
    - Data anonymization option
```

## Security Architecture

### Authentication System

Multi-layered authentication security:

```python
class SecureAuthenticationSystem:
    # Password Security
    PASSWORD_MIN_LENGTH = 12
    PASSWORD_REQUIRE_UPPER = True
    PASSWORD_REQUIRE_LOWER = True
    PASSWORD_REQUIRE_NUMBER = True
    PASSWORD_REQUIRE_SPECIAL = True
    
    def hash_password(self, password: str) -> str:
        """Hash password using bcrypt with salt"""
        return bcrypt.hashpw(
            password.encode('utf-8'),
            bcrypt.gensalt(rounds=12)
        ).decode('utf-8')
    
    def verify_password(self, password: str, hash: str) -> bool:
        """Verify password with timing attack protection"""
        return bcrypt.checkpw(
            password.encode('utf-8'),
            hash.encode('utf-8')
        )
    
    def generate_session_token(self) -> str:
        """Generate cryptographically secure session token"""
        return secrets.token_urlsafe(32)
```

### Authorization Model

Role-based access control (RBAC):

```python
# Permission Matrix
PERMISSIONS = {
    'admin': {
        'system_config': ['read', 'write'],
        'all_users': ['read', 'write'],
        'all_courses': ['read'],
        'ai_models': ['read', 'write', 'delete']
    },
    'instructor': {
        'own_courses': ['read', 'write', 'delete'],
        'own_students': ['read', 'invite', 'remove'],
        'own_ai_models': ['read', 'write'],
        'student_submissions': ['read'],
        'feedback': ['read', 'write', 'approve']
    },
    'student': {
        'enrolled_courses': ['read'],
        'own_submissions': ['read', 'write'],
        'own_feedback': ['read'],
        'own_progress': ['read']
    }
}

def check_permission(user_role: str, resource: str, action: str) -> bool:
    """Check if role has permission for resource action"""
    role_perms = PERMISSIONS.get(user_role, {})
    resource_perms = role_perms.get(resource, [])
    return action in resource_perms
```

### Session Security

Secure session management:

```python
class SecureSessionManager:
    # Session Configuration
    SESSION_LIFETIME = 86400  # 24 hours
    SESSION_COOKIE_SECURE = True  # HTTPS only
    SESSION_COOKIE_HTTPONLY = True  # No JS access
    SESSION_COOKIE_SAMESITE = 'Lax'  # CSRF protection
    
    def create_session(self, user_email: str) -> str:
        """Create secure session"""
        session_id = secrets.token_urlsafe(32)
        
        session_data = {
            'id': session_id,
            'user': user_email,
            'created': datetime.utcnow(),
            'last_active': datetime.utcnow(),
            'ip_address': request.remote_addr,
            'user_agent': request.user_agent.string
        }
        
        # Store encrypted session
        encrypted = self.encrypt_session(session_data)
        cache.set(f"session:{session_id}", encrypted, self.SESSION_LIFETIME)
        
        return session_id
    
    def validate_session(self, session_id: str) -> Optional[dict]:
        """Validate and refresh session"""
        encrypted = cache.get(f"session:{session_id}")
        if not encrypted:
            return None
            
        session_data = self.decrypt_session(encrypted)
        
        # Check expiration
        if (datetime.utcnow() - session_data['created']).seconds > self.SESSION_LIFETIME:
            self.destroy_session(session_id)
            return None
        
        # Update last active
        session_data['last_active'] = datetime.utcnow()
        encrypted = self.encrypt_session(session_data)
        cache.set(f"session:{session_id}", encrypted, self.SESSION_LIFETIME)
        
        return session_data
```

## Data Encryption

### Encryption at Rest

Sensitive data encryption in database:

```python
class EncryptionService:
    def __init__(self):
        # Derive key from secret
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=settings.ENCRYPTION_SALT.encode(),
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(
            kdf.derive(settings.SECRET_KEY.encode())
        )
        self.cipher = Fernet(key)
    
    def encrypt_field(self, data: str) -> str:
        """Encrypt sensitive field"""
        if not data:
            return data
        return self.cipher.encrypt(data.encode()).decode()
    
    def decrypt_field(self, encrypted: str) -> str:
        """Decrypt sensitive field"""
        if not encrypted:
            return encrypted
        return self.cipher.decrypt(encrypted.encode()).decode()

# Usage for API keys
class AIModelSecure(AIModel):
    def save_api_key(self, api_key: str):
        self.api_config['api_key'] = encryption.encrypt_field(api_key)
    
    def get_api_key(self) -> str:
        encrypted = self.api_config.get('api_key', '')
        return encryption.decrypt_field(encrypted)
```

### Encryption in Transit

All data transmitted securely:

```yaml
HTTPS Configuration:
  TLS Version: 1.2 minimum, 1.3 preferred
  Cipher Suites: Modern secure suites only
  HSTS: Enabled with preload
  Certificate: Valid CA-signed cert
  
Security Headers:
  Strict-Transport-Security: max-age=31536000
  X-Content-Type-Options: nosniff
  X-Frame-Options: DENY
  X-XSS-Protection: 1; mode=block
  Content-Security-Policy: default-src 'self'
```

## Input Validation & Sanitization

### Input Validation

Comprehensive validation for all inputs:

```python
class InputValidator:
    # Email validation
    EMAIL_REGEX = re.compile(r'^[\w\.-]+@[\w\.-]+\.\w+$')
    
    # File upload validation
    ALLOWED_EXTENSIONS = {'.pdf', '.docx', '.txt'}
    MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
    
    @staticmethod
    def validate_email(email: str) -> bool:
        """Validate email format and domain"""
        if not InputValidator.EMAIL_REGEX.match(email):
            return False
        
        # Check against domain whitelist if enabled
        domain = email.split('@')[1]
        if settings.ENFORCE_DOMAIN_WHITELIST:
            return domain in get_whitelisted_domains()
        
        return True
    
    @staticmethod
    def validate_file_upload(file) -> Tuple[bool, str]:
        """Validate uploaded file"""
        # Check extension
        ext = Path(file.filename).suffix.lower()
        if ext not in InputValidator.ALLOWED_EXTENSIONS:
            return False, "File type not allowed"
        
        # Check size
        file.seek(0, 2)  # Seek to end
        size = file.tell()
        file.seek(0)  # Reset
        
        if size > InputValidator.MAX_FILE_SIZE:
            return False, "File too large"
        
        # Check MIME type
        mime = magic.from_buffer(file.read(1024), mime=True)
        file.seek(0)
        
        allowed_mimes = {
            'application/pdf',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'text/plain'
        }
        
        if mime not in allowed_mimes:
            return False, "Invalid file content"
        
        return True, "Valid"
```

### Output Sanitization

Prevent XSS attacks:

```python
class OutputSanitizer:
    @staticmethod
    def sanitize_html(text: str) -> str:
        """Remove dangerous HTML"""
        # Allow only safe tags
        allowed_tags = ['p', 'br', 'strong', 'em', 'u', 'ol', 'ul', 'li']
        allowed_attrs = {}
        
        return bleach.clean(
            text,
            tags=allowed_tags,
            attributes=allowed_attrs,
            strip=True
        )
    
    @staticmethod
    def escape_for_display(text: str) -> str:
        """Escape for safe display"""
        return html.escape(text, quote=True)
```

## SQL Injection Prevention

### Parameterized Queries

All database queries use parameters:

```python
# NEVER do this
bad_query = f"SELECT * FROM users WHERE email = '{email}'"

# ALWAYS do this
safe_query = "SELECT * FROM users WHERE email = ?"
result = db.execute(safe_query, (email,))

# ORM automatically parameterizes
user = User.get(email=email)  # Safe
```

### ORM Security

FastLite ORM provides automatic protection:

```python
class SecureModelBase:
    @classmethod
    def get_by_id(cls, id: int, user: User) -> Optional['Model']:
        """Get with access control"""
        obj = cls.get(id)
        if not obj:
            return None
            
        # Check ownership
        if not cls.user_can_access(obj, user):
            raise PermissionDenied()
            
        return obj
    
    @classmethod
    def user_can_access(cls, obj: 'Model', user: User) -> bool:
        """Override in subclasses"""
        raise NotImplementedError
```

## API Security

### Rate Limiting

Prevent abuse and DoS:

```python
from functools import wraps
from collections import defaultdict
import time

class RateLimiter:
    def __init__(self, requests_per_minute=60):
        self.requests_per_minute = requests_per_minute
        self.requests = defaultdict(list)
    
    def limit(self, f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            # Get client identifier
            client_id = request.remote_addr
            if session.get('auth'):
                client_id = session['auth']
            
            # Clean old requests
            now = time.time()
            minute_ago = now - 60
            self.requests[client_id] = [
                req_time for req_time in self.requests[client_id]
                if req_time > minute_ago
            ]
            
            # Check limit
            if len(self.requests[client_id]) >= self.requests_per_minute:
                return "Rate limit exceeded", 429
            
            # Record request
            self.requests[client_id].append(now)
            
            return f(*args, **kwargs)
        return wrapper

# Usage
rate_limiter = RateLimiter(requests_per_minute=60)

@rt('/api/submit')
@rate_limiter.limit
def submit_draft():
    # Handle submission
    pass
```

### CSRF Protection

Cross-site request forgery prevention:

```python
class CSRFProtection:
    @staticmethod
    def generate_token() -> str:
        """Generate CSRF token"""
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def validate_token(token: str) -> bool:
        """Validate CSRF token"""
        session_token = session.get('csrf_token')
        if not session_token or not token:
            return False
        return secrets.compare_digest(session_token, token)
    
    @staticmethod
    def protect(f):
        """Decorator for CSRF protection"""
        @wraps(f)
        def wrapper(*args, **kwargs):
            if request.method == 'POST':
                token = request.form.get('csrf_token')
                if not CSRFProtection.validate_token(token):
                    return "CSRF validation failed", 403
            return f(*args, **kwargs)
        return wrapper
```

## Audit Logging

### Security Audit Trail

Comprehensive logging of security events:

```python
class SecurityAuditor:
    @staticmethod
    async def log_event(
        event_type: str,
        user: str,
        details: dict,
        severity: str = 'INFO'
    ):
        """Log security event"""
        event = {
            'timestamp': datetime.utcnow().isoformat(),
            'type': event_type,
            'user': user,
            'ip_address': request.remote_addr,
            'user_agent': request.user_agent.string,
            'details': details,
            'severity': severity
        }
        
        # Store in database
        await db.audit_logs.insert(**event)
        
        # Alert on critical events
        if severity == 'CRITICAL':
            await alert_security_team(event)

# Usage examples
await SecurityAuditor.log_event(
    'login_success',
    user_email,
    {'method': 'password'},
    'INFO'
)

await SecurityAuditor.log_event(
    'permission_denied',
    user_email,
    {'resource': 'admin_dashboard', 'action': 'access'},
    'WARNING'
)

await SecurityAuditor.log_event(
    'api_key_accessed',
    admin_email,
    {'model_id': model_id, 'purpose': 'configuration'},
    'INFO'
)
```

### Audit Log Retention

Secure retention and rotation:

```yaml
Audit Log Policy:
  Retention Period: 365 days
  Rotation: Monthly
  Archive: Encrypted backups
  Access: Admins only
  
Logged Events:
  - Authentication (success/failure)
  - Authorization (granted/denied)
  - Data access (read/write/delete)
  - Configuration changes
  - API key operations
  - Security violations
```

## Incident Response

### Security Incident Procedures

Defined response procedures:

```yaml
Incident Response Plan:
  Detection:
    - Automated monitoring alerts
    - User reports
    - Log analysis
    
  Assessment:
    - Severity classification
    - Impact analysis
    - Scope determination
    
  Containment:
    - Isolate affected systems
    - Disable compromised accounts
    - Block malicious IPs
    
  Remediation:
    - Apply security patches
    - Reset affected credentials
    - Review and update controls
    
  Recovery:
    - Restore normal operations
    - Verify security
    - Monitor for recurrence
    
  Lessons Learned:
    - Document incident
    - Update procedures
    - Improve controls
```

### Emergency Procedures

Quick response capabilities:

```python
class EmergencySecurityControls:
    @staticmethod
    async def lockdown_mode():
        """Enable emergency lockdown"""
        # Disable new registrations
        await db.system_config.update(
            key='allow_registration',
            value='false'
        )
        
        # Force all users to re-authenticate
        await cache.clear_pattern('session:*')
        
        # Disable API access
        await db.system_config.update(
            key='api_enabled',
            value='false'
        )
        
        # Alert administrators
        await send_emergency_alerts(
            "System in lockdown mode"
        )
    
    @staticmethod
    async def disable_user(email: str, reason: str):
        """Emergency user disable"""
        # Update user status
        await db.users.update(
            email=email,
            status='suspended',
            suspension_reason=reason
        )
        
        # Clear all sessions
        await clear_user_sessions(email)
        
        # Log action
        await SecurityAuditor.log_event(
            'emergency_user_disable',
            'system',
            {'user': email, 'reason': reason},
            'CRITICAL'
        )
```

## Compliance & Standards

### Privacy Compliance

Alignment with privacy regulations:

```yaml
GDPR Compliance:
  - Explicit consent for data processing
  - Right to access personal data
  - Right to rectification
  - Right to erasure (with limitations)
  - Data portability
  - Privacy by design
  
FERPA Compliance:
  - Educational records protection
  - Limited access to student data
  - Audit trails for access
  - Secure data transmission
  - Parent/guardian access controls
```

### Security Standards

Following industry best practices:

```yaml
OWASP Top 10 Mitigation:
  A01:2021 – Broken Access Control: RBAC implementation
  A02:2021 – Cryptographic Failures: Strong encryption
  A03:2021 – Injection: Parameterized queries
  A04:2021 – Insecure Design: Security architecture
  A05:2021 – Security Misconfiguration: Secure defaults
  A06:2021 – Vulnerable Components: Regular updates
  A07:2021 – Auth Failures: Strong authentication
  A08:2021 – Software Integrity: Code signing
  A09:2021 – Logging Failures: Comprehensive audit
  A10:2021 – SSRF: Input validation
```

## Security Checklist

### Deployment Security

Pre-deployment verification:

- [ ] HTTPS enabled with valid certificate
- [ ] Security headers configured
- [ ] Database encrypted (if supported)
- [ ] Backup encryption enabled
- [ ] Admin accounts use strong passwords
- [ ] Domain whitelist configured
- [ ] Rate limiting enabled
- [ ] Audit logging active
- [ ] Monitoring alerts configured
- [ ] Incident response plan documented
- [ ] Security training completed
- [ ] Penetration testing performed

### Ongoing Security

Regular security tasks:

- [ ] Weekly: Review audit logs
- [ ] Monthly: Update dependencies
- [ ] Quarterly: Rotate API keys
- [ ] Annually: Security audit
- [ ] As needed: Apply security patches

---

{: .warning }
> Security is an ongoing process. Regular reviews, updates, and training are essential to maintain a secure system.

{: .note }
> This security architecture provides defense-in-depth protection while maintaining usability for educational purposes.