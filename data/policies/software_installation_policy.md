# Software Installation & Approved Applications Policy

**Document ID:** IT-POL-007
**Last Updated:** 2026-02-20
**Owner:** IT Security & Engineering Platform Team

## 1. Approved Software Catalog
Employees may self-install any application listed in the Internal Software Catalog
(catalog.corp.example.com) without additional approval. This includes common
productivity, design, and developer tools that have already passed a security review.

## 2. Requesting New Software
Software not in the catalog requires a Software Request ticket, which triggers an
automatic security and license review. Typical turnaround is 3-5 business days for
standard SaaS tools, and 10-15 business days for anything requiring a security
architecture review (e.g., tools with access to customer data, or that require
elevated system permissions).

## 3. Prohibited Software
The following categories are prohibited on all company devices unless an explicit
exception is granted by the CISO:
- Unlicensed / pirated software of any kind.
- Peer-to-peer file sharing clients.
- Remote access tools not on the approved list (e.g., unapproved screen-sharing or
  remote desktop software) other than the corporate-standard tool (TeamViewer
  Enterprise, IT-managed only).
- Browser extensions requesting broad data-access permissions that have not been
  reviewed by IT Security.

## 4. Open Source & Developer Tooling
Engineers may install standard developer tooling (IDEs, language runtimes, package
managers, containers) on engineering-issued laptops without a ticket, provided it
comes from an official/verified source. Installing packages from unverified or
unofficial third-party repositories requires review.

## 5. Administrative/Local Admin Rights
Standard employees do not have local admin rights by default. Engineering roles
receive scoped admin rights via the Engineering Laptop Profile, which still blocks
disabling of endpoint security agents (CrowdStrike, disk encryption).
