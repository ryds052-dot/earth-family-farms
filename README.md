# Earth Family Farms

A beginner-friendly Flask landing page for a family eco-farm in St. Ann, Jamaica.

## Project structure

```text
code/
├── app.py                 # Flask routes, validation, and SQLite database helpers
├── farm.db                # Created automatically when the app first runs
├── requirements.txt       # Python packages the project needs
├── README.md              # Setup instructions
└── templates/
    └── index.html         # Landing page HTML and Tailwind CSS
```

## Run the page locally

1. Install Python from [python.org](https://www.python.org/downloads/). During installation on Windows, check **Add Python to PATH**.
2. Open PowerShell in this folder:

   ```powershell
   cd C:\Users\ryder\Downloads\code
   ```

3. Create a virtual environment. This gives the project its own isolated Python packages:

   ```powershell
   python -m venv .venv
   ```

4. Activate the environment:

   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

   If PowerShell blocks activation, run:

   ```powershell
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   ```

   Then run the activation command again.

5. Install Flask:

   ```powershell
   pip install -r requirements.txt
   ```

6. Start the development server:

   ```powershell
   python app.py
   ```

7. Open `http://127.0.0.1:5000` in your browser.

## How the first Flask file works

- `Flask(__name__)` creates the web application.
- `@app.route("/")` says that the `home` function responds to the website's home address.
- `render_template("index.html")` loads the HTML file from the `templates` folder.
- `app.run(debug=True)` starts a local server and refreshes it when you save changes.
- `farm.db` is created automatically the first time Flask starts.

## Test a booking

1. Start the app with `python app.py`.
2. Open `http://127.0.0.1:5000/#book`.
3. Complete the booking form with a cabin, name, email, and two dates.
4. Submit the form. A success message appears and the reservation is stored in `farm.db`.
5. Submit the same cabin with overlapping dates again. The app will reject it.

The server uses parameterized SQLite queries, validates dates on the server (not only in
the browser), and accepts a new check-in on the same day as another guest's check-out.
The development secret key in `app.py` should be replaced with a private environment
variable before deploying publicly.

The Tailwind CSS CDN is loaded by `index.html`, so this first version does not need a separate CSS build step. The photo URLs are temporary Unsplash images and should be replaced with licensed farm photography before launch.
