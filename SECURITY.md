# Security Policy

## Supported state

Kyra is a pre-release university research prototype. No release is currently supported for production surveillance or safety-critical operation.

## Reporting

Do not open a public issue for secrets, private footage, identity data, dependency compromise, or an exploitable vulnerability. Use the private repository's GitHub Security Advisory reporting flow and notify the repository steward. Include the affected commit, minimal reproduction, impact, and safe remediation suggestion without uploading private datasets.

## Data and secret rules

- Never commit credentials, bearer tokens, `.env` files, private RGB-D recordings, or identifiable person data.
- Use deterministic synthetic/tiny reviewed fixtures in normal CI.
- Keep model weights, datasets, generated runs, and point clouds outside Git with provenance/checksum records.
- Treat untrusted manifests, paths, images, and serialized arrays as hostile input; reject traversal, unsupported schemas, invalid shapes/types, and unsafe sizes.
- A security fix does not bypass shared-contract approval when it changes persisted or public meaning; fail closed while the coordinated fix is reviewed.
