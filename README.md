# Earth Family Farms

A Flask site for Earth Family Farms in Ocho Rios, St. Ann, Jamaica. The site
includes sanctuary and estate showcases, an accessible image lightbox, and
stay/experience inquiry forms delivered through Resend.

## Project structure

```text
app.py                 Flask routes and server-side form validation
requirements.txt       Python runtime dependencies
package.json           Tailwind CSS build script and development dependency
static/
  css/site.css         Shared visual system
  css/tailwind.css     Compiled local Tailwind utilities
  css/tailwind.input.css Tailwind CSS build entrypoint
  js/site.js           Shared image lightbox interactions
  images/              Site photography and brand assets
templates/             Jinja page templates
tests/test_app.py      Route and booking-flow tests
```

## Local setup

Create and activate a virtual environment, then install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Tailwind utilities are built and served locally; no runtime CDN compilation is
required. To rebuild them after changing template utility classes:

```powershell
npm ci
npm run build:css
```

Run the application:

```powershell
python app.py
```

The local site is available at `http://127.0.0.1:5000`. Set `FLASK_DEBUG=true`
only for local development when an interactive debugger is needed.

## Booking inquiries

The stays and experience inquiry form sends validated submissions through
Resend. Configure these environment variables in the deployment environment:

- `RESEND_API_KEY` — API key for sending booking inquiries.
- `BOOKING_EMAIL` — inbox that receives inquiries.
- `RESEND_FROM_EMAIL` — verified sender address (defaults to Resend's
  onboarding sender).

Without both `RESEND_API_KEY` and `BOOKING_EMAIL`, the form returns a clear
service-unavailable message and visitors can use the WhatsApp booking link
instead.

## Investor and harvest inquiry portals

- `/invest` and `/estate-parcels` provide the interactive parcel scenario and
  a consent-gated offering-memorandum / parcel-interest inquiry. The $25,000
  per-acre assumption, 5% annual appreciation assumption, and use-specific
  gross yields are illustrative only; they are not approved pricing,
  appraisals, or promised returns.
- `/harvest` and `/wholesale` provide a sample seasonal pipeline and validated
  bulk-order inquiry builder. Product volumes and planning windows are
  demonstration data, not inventory or supply commitments.
- `/vitals` provides the same sample sustainability panel included on the
  homepage. Its sensor and weather values are simulated and are not connected
  to live estate monitoring.

Investor and wholesale forms validate submissions on the server and then
redirect to a prefilled WhatsApp draft for the concierge at +1 876-287-4304.
Visitors must confirm and send each message in WhatsApp; the site does not send
messages automatically.

Run the test suite with:

```powershell
python -m unittest discover -s tests
```
