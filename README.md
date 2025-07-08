#  Veritas: AI-Powered Compliance Automation using IBM Granite & RAG

![Veritas Banner](https://img.shields.io/badge/Compliance-Automation-blueviolet)  
An AI-first compliance orchestration system that makes regulatory alignment a built-in process — not an afterthought.

## Demo
[![Watch the demo video](https://img.youtube.com/vi/7F_1nWdgSo8/0.jpg)](https://youtu.be/7F_1nWdgSo8?si=PIePfoJ_SFS4bMnI)


---

##  Problem Statement

With increasing global (GDPR, ISO/IEC 27001) and regional (India’s PDPB, CERT-In) regulations, most software teams still handle compliance reactively:

-  Hastily generated documents
-  Missed deadlines and incomplete evidence
-  Legal, financial, and reputational risk
-  Product launch delays and overburdened teams

This issue is **amplified in AI, fintech, and public sectors**, where compliance is expected **by design**.

---

## Solution – What Veritas Does

Veritas integrates **compliance intelligence** throughout the **software delivery lifecycle (SDLC)**.  
It continuously analyzes project artifacts (code, configs, docs) and uses **AI + RAG** to:

✅ Highlight violations  
✅ Confirm tested regulatory controls  
✅ Translate legal clauses into actionable technical items  
✅ Generate structured remediation tasks for traceability  

> Veritas empowers security teams, developers, and compliance leaders to stay audit-ready — all the time.

---

##  Key Features

-  **Real-time Regulatory Validation** during CI/CD
-  **RAG-based Legal Context** mapped to your artifacts
-  **Automated Report Generation** for 56+ compliance documents
-  Gap Detection in privacy, RBAC, and authority policies
-  Dashboards for CISOs and stakeholders
-  Integration with existing SDLC tools

---

## 🛡️ IBM Granite Usage

This project leverages **IBM WatsonX Granite Models** with LangChain for advanced reasoning:

| Feature | IBM Granite Component |
|--------|------------------------|
|  Dynamic Task Assignment | `Granite Orchestration` |
|  Document Analysis | `Granite-3-2b Instruct` |
|  Source Code & Config Scanning | `Granite Code` |
|  Regulation-grounded RAG | `LangChain + Granite` |
|  Long-context reasoning | `Granite-3-2b-instruct` |

---

##  Tech Stack

| Layer | Technology |
|------|------------|
| Frontend | React.js (Vite) |
| Backend | Python Flask |
| AI/LLM | IBM Granite (WatsonX), LangChain |
| File Parsing | PyPDF, Python-docx, Openpyxl |
| Infra | Docker, Flask-CORS, dotenv |

---

##  Directory Structure

##  Setup Instructions

### 1. Clone the repo

```bash
git clone https://github.com/SandeshKhilari01/Veritas-IBM-TechXChange2025.git
cd veritas
```

---

##  Backend Setup

```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file and add your IBM WatsonX credentials:

```
WATSONX_API_KEY=your_api_key
WATSONX_URL=https://your-region.ml.cloud.ibm.com
```

Then run the backend server:

```bash
python main.py
```

## 🌐 Frontend Setup

```bash
cd frontend
npm install
npm run dev
```
Make sure your backend has CORS enabled for this frontend origin.

---

## Example APIs

| Endpoint                 | Method | Description                                   |
| ------------------------ | ------ | --------------------------------------------- |
| `/setup_ingestion`       | POST   | Initialize ingestion with company description |
| `/upload`                | POST   | Upload compliance documents                   |
| `/process_files`         | POST   | Extract and index files                       |
| `/analyze/<regulation>`  | POST   | Analyze compliance with given regulation      |
| `/generate_report`       | POST   | Generate final audit report                   |
| `/status`                | GET    | Get analysis progress                         |
| `/available_regulations` | GET    | List supported regulations                    |
| `/reset`                 | POST   | Reset analysis session                        |


This project is licensed under the **MIT License**.

---

##  Acknowledgments

*  IBM WatsonX Granite for enabling powerful legal-to-technical AI
*  LangChain for orchestrating document intelligence with LLMs
*  OpenAI & Python OSS for ecosystem tools
*  Team Veritas for building this end-to-end AI compliance platform
*  ## ASHITOSH, GANESH, DHRUVRAJ, PRADEEP, PRATHMESH, SAHIL (TECH AVINYA)
