# OpenAI credential preflight: Keychain prompt truncation

The macOS `security add-generic-password ... -w` hidden prompt silently stores
only 128 characters. Reproduced with a 164-character dummy credential: retrieval
returned 128 characters. The actual OpenAI item was also 128 characters, explaining
the repeated `401 invalid_api_key` responses after Scott correctly replaced it.
Earlier suggestions to regenerate the credential did not address this storage bug.

Use `python3 scripts/store_openai_keychain.py` from the repository root instead.
It reads hidden input with Python getpass and writes through the native Security
framework, without putting credentials in subprocess arguments or shell history.
Native add, update and read were verified with 164- and 200-character dummy values.
All disposable test items were removed. The real stored credential was not modified
by diagnostics. Updating the existing item preserves its access attributes.

A newly created native item may require macOS Keychain access approval when read
by another executable. The existing security-created OpenAI item is updated in
place. Do not use the truncated CLI prompt for long provider credentials.

No Sol inference requests have run. Restore the full credential through the helper,
then repeat authentication preflight before running smoke and full evaluations.
