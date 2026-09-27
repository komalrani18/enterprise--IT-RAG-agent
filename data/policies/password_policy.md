# Password & Authentication Policy

**Document ID:** IT-POL-002
**Last Updated:** 2025-11-02
**Owner:** IT Security

## 1. Password Requirements
- Minimum 14 characters, including at least one uppercase letter, one number, and one
  special character.
- Passwords must not reuse any of the last 10 passwords used on the account.
- Passwords expire every 180 days for standard accounts and every 90 days for accounts
  with administrative/privileged access.

## 2. Multi-Factor Authentication (MFA)
MFA is mandatory for all corporate accounts, including email, VPN, and the internal
HR portal. Approved MFA methods are: hardware security keys (YubiKey, preferred),
the Okta Verify mobile app, or SMS as a last resort (SMS-based MFA is being phased
out by end of 2026 due to SIM-swap risk).

## 3. Self-Service Password Reset
Employees can reset a forgotten password themselves at reset.corp.example.com using
their recovery email and MFA device. If MFA is also unavailable (e.g., lost phone),
employees must contact the IT Help Desk and verify identity via manager confirmation
or an in-person ID check for on-site staff.

## 4. Shared / Service Accounts
Shared logins are prohibited except for designated service accounts, which must be
registered with IT Security, use randomly generated 32+ character passwords stored in
the corporate password vault (1Password Business), and be rotated every 90 days.

## 5. Locked Account Policy
Accounts lock automatically after 5 failed login attempts within 15 minutes. Locked
accounts unlock automatically after 30 minutes, or immediately via IT Help Desk after
identity verification.
