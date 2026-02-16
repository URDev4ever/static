<h1 align="center">Static</h3>
<p align="center"> 🇺🇸 <a href="README.md"><b>English</b></a> | 🇪🇸 <a href="README_ES.md">Español</a> </p>
<p align="center">
  <img width="358" height="197" alt="static banner" src="https://github.com/user-attachments/assets/a488bd7e-d760-451e-974b-5fd852077d76" />
</p>

**Static** is a lightweight, dependency-free **typosquatting reconnaissance tool** written in pure Python. It generates common typo variations of a target domain and checks them using DNS and HTTP/HTTPS heuristics to identify potentially available domains and redirect behavior.

Designed for **security testing, OSINT, and defensive research**, Static focuses on clarity, stability, and clean terminal output.

---

## ✨ Features

* Zero dependencies (Python standard library only)
* Multiple typo generation techniques
* DNS resolution checks
* HTTP/HTTPS probing with redirect detection
* Clean real-time progress display (spinner + progress bar)
* Graceful Ctrl+C handling with partial results
* Cross-platform (Linux, macOS, Windows)
  
---

## 🛠️ Installation

No installation required

Just clone the repository and run the script:

```bash
git clone https://github.com/urdev4ever/static.git
cd static
python3 static.py
```

Python **3.8+** recommended.

---

## 🚀 Usage

```bash
python3 static.py -d target.com
```

### Example

```bash
python3 static.py -d google.com
```

<img width="508" height="339" alt="static scanning" src="https://github.com/user-attachments/assets/0ba76b64-b38d-41e4-a40a-248dc0f6b016" />

During execution, Static will:

1. Generate typo-based domain variants
2. Check DNS resolution
3. Probe HTTP and HTTPS endpoints
4. Display real-time progress
5. Output categorized results

---

## 🧠 How It Works

Static uses a heuristic-based approach:

### Typo Generation

* Character deletion
* Character duplication
* Adjacent character swap
* QWERTY keyboard adjacency replacement
* Common TLD variations (`.com`, `.net`, `.org`, `.co`, `.io`)
* Dot removal in multi-level domains

### Domain Verification Logic

* **No DNS resolution** → Marked as *Potentially Available*
* **DNS resolves + HTTP redirect** → Marked as *Redirect*
* **DNS resolves + HTTP responds** → Marked as *Taken*

> Note: “Potentially available” does **not** guarantee availability. Final verification should be done via WHOIS or a registrar.

---

## 📊 Output Categories

* **Potentially Available Domains**

  * No DNS resolution detected

* **Redirecting Domains**

  * Domains that redirect to a different host

* **Taken Domains**

  * Domains resolving and responding normally

A summary with scan duration and speed is shown at the end.


<img width="424" height="547" alt="static results" src="https://github.com/user-attachments/assets/123f512d-a7fc-4156-ab61-764ea079c07e" />

---

## 🔐 SSL Note

SSL certificate verification is intentionally disabled for HTTPS checks. This is done to ensure stability and coverage during reconnaissance and avoid failures caused by misconfigured certificates.

---

## 🧪 Requirements

* Python 3.x
* No external libraries
* No API keys
* No configuration files

---

## 🧭 Roadmap / Future Improvements

The following features are planned for future versions:

* Custom TLD selection via flags (e.g. `--tlds com,net,org`)
* Option to disable HTTP probing (`--no-http`)
* JSON output mode for automation and pipelines
* File output support (`--output results.txt` / `.json`)
* Optional multi-threaded scanning with rate limits
* Additional typo techniques
* Improved domain availability heuristics

These features will be introduced gradually while keeping the tool lightweight and dependency-free.

---

## ⚠️ Disclaimer

Static is intended for **defensive security testing, research, and educational purposes only**. The author does not condone or support malicious use.

You are responsible for complying with all applicable laws and regulations.

---

## ⭐ Contributing

Pull requests are welcome if they:

* Improve typo-generation techniques or domain verification heuristics without adding external dependencies
* Enhance scanning stability, performance, or output clarity while preserving clean terminal UX
* Maintain the lightweight, dependency-free philosophy of the tool and avoid feature bloat

---
made with <3 by URDev
