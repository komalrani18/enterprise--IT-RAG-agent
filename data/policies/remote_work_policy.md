# Remote Work & VPN Access Policy

**Document ID:** HR-POL-014
**Last Updated:** 2026-01-10
**Owner:** People Operations & IT Security

## 1. Eligibility
Full-time employees who have completed their 90-day probationary period are eligible
to work remotely up to 3 days per week, subject to manager approval. Contractors and
interns require explicit written approval from both their manager and IT Security.

## 2. Required Equipment
Remote employees must use a company-issued laptop with full-disk encryption enabled.
Personal devices ("BYOD") may only be used for email and calendar access via the
approved Mobile Device Management (MDM) profile — never for accessing internal
engineering repositories or customer data systems.

## 3. VPN Requirements
- All remote connections to internal systems (Git, internal wikis, databases, admin
  panels) MUST go through the corporate VPN (GlobalProtect).
- VPN sessions automatically time out after 8 hours of inactivity and require
  re-authentication with SSO + hardware security key (YubiKey).
- Split-tunneling is disabled by default; requests for split-tunnel exceptions must be
  filed with IT Security and approved by the CISO's office.

## 4. Network Requirements
Employees working remotely must not connect to internal systems over public/unsecured
Wi-Fi (e.g., cafes, airports) without VPN active. Home networks should use WPA2/WPA3
encryption at minimum.

## 5. Incident Reporting
If a company laptop is lost, stolen, or suspected compromised, the employee must
notify IT Security within 1 hour via the emergency line (ext. 4357) and file an
incident ticket. Remote access credentials will be revoked immediately upon report.
