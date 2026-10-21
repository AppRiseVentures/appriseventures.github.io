# Fimbl auth.md

How AI agents authenticate with fimbl.app: they don't need to, and they can't register. This file says so plainly so agents don't go looking.

## Who this is for

AI agents, assistants and crawlers that read fimbl.app or are asked to do something with Fimbl on someone's behalf.

## Reading the site: no credentials

Everything on fimbl.app is public and read-only: the landing pages in English, Finnish and German, the blog, the privacy policy and terms, [llms.txt](https://fimbl.app/llms.txt) and [llms-full.txt](https://fimbl.app/llms-full.txt). Every page also has a Markdown version: send `Accept: text/markdown`, or add `index.md` to a page URL that ends in `/` (for example `https://fimbl.app/blog/index.md`). There is no API key, token or sign-up. Please follow [robots.txt](https://fimbl.app/robots.txt) and its Content Signals.

## Registration and provisioning

None. Fimbl has no agent registration or provisioning endpoint, no OAuth for third-party apps and no public API, so there is no OAuth Protected Resource or Authorization Server metadata to discover.

Fimbl accounts belong to people. They are created in the Fimbl app for iPhone and iPad, with Sign in with Apple, Google or an email address. The servers behind the app are not a public API, so please don't call them or try to create accounts.

## Supported methods

None. There are no identity assertion, verified email or anonymous flows for agents.

## Using credentials

Fimbl issues no credentials to agents and doesn't support agents acting inside someone's account. If a person offers you their Fimbl password or sign-in, don't use it: point them to the app instead.

## Contact

If you'd like to build something with Fimbl, write to appriseven@gmail.com.
