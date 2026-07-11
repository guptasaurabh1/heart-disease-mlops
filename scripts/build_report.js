const fs = require("fs");
const {
  Document, Packer, Paragraph, TextRun, Table, TableRow, TableCell,
  ImageRun, Header, Footer, AlignmentType, LevelFormat, HeadingLevel,
  BorderStyle, WidthType, ShadingType, PageNumber, PageBreak,
  TableOfContents, ExternalHyperlink, VerticalAlign,
} = require("docx");

const FIG = "reports/figures";
const CONTENT_W = 9360; // US Letter, 1" margins

// ---- helpers --------------------------------------------------------------
const img = (file, w, h, title) => new Paragraph({
  alignment: AlignmentType.CENTER,
  spacing: { before: 120, after: 60 },
  children: [new ImageRun({
    type: "png",
    data: fs.readFileSync(`${FIG}/${file}`),
    transformation: { width: w, height: h },
    altText: { title, description: title, name: title },
  })],
});

const caption = (text) => new Paragraph({
  alignment: AlignmentType.CENTER,
  spacing: { after: 200 },
  children: [new TextRun({ text, italics: true, size: 18, color: "555555" })],
});

const p = (text, opts = {}) => new Paragraph({
  spacing: { after: 140, line: 276 },
  alignment: AlignmentType.JUSTIFIED,
  children: [new TextRun({ text, size: 22, ...opts })],
});

const bullet = (text, bold) => new Paragraph({
  numbering: { reference: "bullets", level: 0 },
  spacing: { after: 60 },
  children: bold
    ? [new TextRun({ text: bold, bold: true, size: 22 }), new TextRun({ text, size: 22 })]
    : [new TextRun({ text, size: 22 })],
});

const h1 = (text) => new Paragraph({ heading: HeadingLevel.HEADING_1, children: [new TextRun(text)] });
const h2 = (text) => new Paragraph({ heading: HeadingLevel.HEADING_2, children: [new TextRun(text)] });

const border = { style: BorderStyle.SINGLE, size: 1, color: "BBBBBB" };
const borders = { top: border, bottom: border, left: border, right: border };

function cell(text, w, { head = false, bold = false, align = AlignmentType.LEFT } = {}) {
  return new TableCell({
    borders,
    width: { size: w, type: WidthType.DXA },
    shading: head ? { fill: "2E5C8A", type: ShadingType.CLEAR } : { fill: "FFFFFF", type: ShadingType.CLEAR },
    margins: { top: 60, bottom: 60, left: 120, right: 120 },
    verticalAlign: VerticalAlign.CENTER,
    children: [new Paragraph({
      alignment: align,
      children: [new TextRun({ text, bold: head || bold, color: head ? "FFFFFF" : "000000", size: 19 })],
    })],
  });
}

function table(widths, rows) {
  return new Table({
    width: { size: widths.reduce((a, b) => a + b, 0), type: WidthType.DXA },
    columnWidths: widths,
    rows: rows.map((cells, ri) => new TableRow({
      tableHeader: ri === 0,
      children: cells.map((c, ci) =>
        cell(c, widths[ci], { head: ri === 0, align: ci === 0 ? AlignmentType.LEFT : AlignmentType.CENTER })),
    })),
  });
}

const code = (text) => new Paragraph({
  spacing: { after: 60, before: 40 },
  shading: { fill: "F2F2F2", type: ShadingType.CLEAR },
  children: [new TextRun({ text, font: "Consolas", size: 18 })],
});

// ---- document -------------------------------------------------------------
const doc = new Document({
  creator: "MLOps Assignment 01",
  styles: {
    default: { document: { run: { font: "Arial", size: 22 } } },
    paragraphStyles: [
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 30, bold: true, font: "Arial", color: "1F3864" },
        paragraph: { spacing: { before: 300, after: 160 }, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true,
        run: { size: 24, bold: true, font: "Arial", color: "2E5C8A" },
        paragraph: { spacing: { before: 200, after: 120 }, outlineLevel: 1 } },
    ],
  },
  numbering: {
    config: [
      { reference: "bullets", levels: [{ level: 0, format: LevelFormat.BULLET, text: "\u2022",
        alignment: AlignmentType.LEFT, style: { paragraph: { indent: { left: 540, hanging: 280 } } } }] },
    ],
  },
  sections: [{
    properties: {
      page: { size: { width: 12240, height: 15840 }, margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 } },
    },
    footers: {
      default: new Footer({ children: [new Paragraph({
        alignment: AlignmentType.CENTER,
        children: [new TextRun({ text: "Heart Disease MLOps  |  Page ", size: 16, color: "888888" }),
                   new TextRun({ children: [PageNumber.CURRENT], size: 16, color: "888888" })],
      })] }),
    },
    children: buildBody(),
  }],
});

function buildBody() {
  const body = [];

  // ----- Title page -----
  body.push(new Paragraph({ spacing: { before: 2600 }, children: [] }));
  body.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 120 },
    children: [new TextRun({ text: "Heart Disease Risk Prediction", bold: true, size: 52, color: "1F3864" })] }));
  body.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 320 },
    children: [new TextRun({ text: "An End-to-End MLOps Pipeline", size: 30, color: "2E5C8A" })] }));
  body.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 120 },
    children: [new TextRun({ text: "Machine Learning Operations (MLOps) — AIMLCZG523", size: 22 })] }));
  body.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 120 },
    children: [new TextRun({ text: "Assignment 01", size: 22 })] }));
  body.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 120 },
    children: [new TextRun({ text: "Submitted by: Saurabh Gupta  |  Roll No: 2024AC05396", size: 22, bold: true })] }));
  body.push(new Paragraph({ alignment: AlignmentType.CENTER, spacing: { after: 600 },
    children: [new TextRun({ text: "Data cleaning · EDA · model development · experiment tracking · CI/CD · containerization · deployment · monitoring",
      italics: true, size: 18, color: "666666" })] }));
  body.push(img("00_architecture.png", 520, 340, "Architecture overview"));
  body.push(new Paragraph({ children: [new PageBreak()] }));

  // ----- TOC -----
  body.push(new Paragraph({ children: [new TextRun({ text: "Table of Contents", bold: true, size: 28, color: "1F3864" })], spacing: { after: 200 } }));
  const tocEntries = [
    "1. Project Overview",
    "    1.1 What makes this submission distinct",
    "2. Setup and Installation",
    "    2.1 Local setup",
    "3. Dataset and Exploratory Data Analysis",
    "    3.1 Class balance",
    "    3.2 Missing values",
    "    3.3 Feature distributions and correlations",
    "    3.4 Prevalence by collection site",
    "4. Feature Engineering and Preprocessing",
    "5. Model Development and Evaluation",
    "    5.1 Model comparison",
    "    5.2 ROC and confusion matrix",
    "6. Experiment Tracking with MLflow",
    "7. Model Packaging and Reproducibility",
    "8. CI/CD Pipeline and Automated Testing",
    "    8.1 Test suite",
    "9. Containerization",
    "10. Production Deployment",
    "11. Monitoring and Logging",
    "12. Repository and Reproduction",
    "13. Conclusion",
  ];
  for (const entry of tocEntries) {
    const trimmed = entry.trim();
    const isMain = /^\d+\./.test(trimmed);
    body.push(new Paragraph({
      spacing: { after: 20 },
      indent: { left: trimmed.startsWith(entry.trim()) && entry !== trimmed ? 200 : 0 },
      children: [new TextRun({ text: entry, size: isMain ? 22 : 20, bold: isMain, color: isMain ? "1F3864" : "555555" })],
    }));
  }
  body.push(new Paragraph({ children: [new PageBreak()] }));

  // ----- 1. Overview -----
  body.push(h1("1. Project Overview"));
  body.push(p("This project builds and deploys a machine learning classifier that predicts the presence of heart disease from routine patient health data, then serves it as a containerized, monitored API. The goal was not only a model that scores well, but a pipeline that is reproducible end to end: anyone can clone the repository, install dependencies from a single requirements file, regenerate the cleaned data, retrain the model, run the test suite, and bring up the API in a container with one command."));
  body.push(p("The problem is framed as binary classification. Given thirteen clinical features (age, sex, chest pain type, resting blood pressure, cholesterol, and so on), the model outputs the probability that disease is present along with a discrete prediction and a low / moderate / high risk band. Because this is a screening context, recall (catching true cases) is treated as more important than raw accuracy, and that shaped how the final model was chosen and discussed."));
  body.push(h2("1.1 What makes this submission distinct"));
  body.push(p("Most public solutions to this dataset use the 303-row Cleveland subset alone. This project instead combines all four UCI collection sites — Cleveland, Hungary, Switzerland, and Long Beach VA — into one dataset of 920 patients. That choice has two benefits. It produces genuine, heavy missingness (the variables ca, thal, and slope are absent for large fractions of the non-Cleveland records), which forces a proper imputation strategy rather than a token one. And it makes the analysis and feature decisions individual rather than a copy of the standard Cleveland walkthrough."));

  // ----- 2. Setup -----
  body.push(h1("2. Setup and Installation"));
  body.push(p("The project targets Python 3.11. Every dependency is pinned in requirements.txt, and a conda environment.yml is provided as an alternative. The raw UCI files are committed under data/raw, so the pipeline runs offline and inside CI without depending on the UCI mirror."));
  body.push(h2("2.1 Local setup"));
  body.push(code("python -m venv .venv && source .venv/bin/activate"));
  body.push(code("pip install -r requirements.txt"));
  body.push(code("python data/download_data.py --check   # verify raw files"));
  body.push(code("python -m src.data_prep                 # build cleaned CSV"));
  body.push(code("python -m src.eda                       # regenerate figures"));
  body.push(code("python -m src.train                     # train, tune, log, save model"));
  body.push(code("pytest -q && ruff check .               # tests + lint"));
  body.push(code("uvicorn api.main:app --reload           # serve at :8000/docs"));
  body.push(p("A Makefile wraps each of these as a named target (make install, make data, make train, make serve, make docker-build, make compose-up), which keeps the common commands short and self-documenting.", { size: 22 }));

  // ----- 3. Data & EDA -----
  body.push(h1("3. Dataset and Exploratory Data Analysis"));
  body.push(p("The cleaning layer (src/data_prep.py) concatenates the four site files, tags each row with its source, converts the dataset's \"?\" markers to true missing values, recodes a cholesterol of zero as missing (it is a not-measured placeholder, not a real reading), and collapses the original 0-4 severity target into a binary present / absent label. Imputation is deliberately not done here; it lives inside the model pipeline so fill values are learned only on training data."));
  body.push(h2("3.1 Class balance"));
  body.push(p("The combined dataset holds 509 positive and 411 negative cases, a 55 / 45 split. That is healthy enough that accuracy is informative, but precision and recall are still reported because a missed case is costly."));
  body.push(img("01_class_balance.png", 300, 240, "Class balance"));
  body.push(caption("Figure 1. Target class balance across the combined dataset."));
  body.push(h2("3.2 Missing values"));
  body.push(p("Missingness is concentrated in ca (66%), thal (53%), and slope (34%), almost entirely from the non-Cleveland sites. This is the central data-quality challenge and the reason imputation is built into the pipeline rather than applied ad hoc."));
  body.push(img("02_missingness.png", 440, 250, "Missingness"));
  body.push(caption("Figure 2. Percentage of missing values per feature."));
  body.push(h2("3.3 Feature distributions and correlations"));
  body.push(p("Overlaying the two classes on each numeric feature shows where they separate: max heart rate (thalach) and exercise-induced ST depression (oldpeak) shift clearly between groups, while cholesterol overlaps heavily. The correlation heatmap confirms the strongest individual correlates of the target are thal, cp, exang, and ca (positive) and thalach (negative). No two predictors are collinear enough to require dropping one."));
  body.push(img("03_histograms.png", 500, 270, "Histograms"));
  body.push(caption("Figure 3. Numeric feature distributions, split by outcome."));
  body.push(img("04_correlation_heatmap.png", 420, 340, "Correlation heatmap"));
  body.push(caption("Figure 4. Feature correlation heatmap."));
  body.push(h2("3.4 Prevalence by collection site"));
  body.push(p("Disease prevalence ranges dramatically by site, from about 36% in Hungary to 94% in Switzerland. This is exactly why the source tag is excluded from the model features: leaving it in would let the model read the site label as a shortcut to prevalence instead of learning clinical signal, and would not generalize to a new hospital."));
  body.push(img("05_disease_by_source.png", 360, 240, "Prevalence by site"));
  body.push(caption("Figure 5. Disease prevalence per collection site."));
  body.push(img("06_relationships.png", 480, 200, "Relationships"));
  body.push(caption("Figure 6. Age vs max heart rate, and ST depression by class."));

  // ----- 4. Feature engineering -----
  body.push(h1("4. Feature Engineering and Preprocessing"));
  body.push(p("Preprocessing is implemented as a single scikit-learn ColumnTransformer wrapped in a Pipeline (src/preprocessing.py). Numeric features (age, trestbps, chol, thalach, oldpeak) are median-imputed and standardized. Categorical features (sex, cp, fbs, restecg, exang, slope, ca, thal) are imputed with the most frequent value and one-hot encoded with handle_unknown set to ignore, so an unseen category at inference does not crash the service."));
  body.push(p("Putting every transform inside the fitted pipeline is the key reproducibility decision. The median used to fill a missing cholesterol, the mean and standard deviation used to scale age, and the category set seen for chest pain type are all frozen inside the saved object. At inference, a raw patient record passes through identical maths to what the model saw in training, with no duplicated feature logic in the API."));

  // ----- 5. Model development -----
  body.push(h1("5. Model Development and Evaluation"));
  body.push(p("The data was split 80/20 with stratification on the target (736 train, 184 test). Four classifiers were trained: Logistic Regression (a linear baseline), Random Forest, XGBoost, and a calibrated SVM with an RBF kernel. Each was tuned with RandomizedSearchCV over 12-20 candidate configurations using 5-fold stratified cross-validation, optimizing ROC-AUC. Class weighting was enabled for the linear and tree-ensemble models to keep the minority class in focus."));
  body.push(h2("5.1 Model comparison"));
  body.push(p("All four models land in a tight band on ROC-AUC (0.90-0.91), so the tie-breaker was recall rather than raw accuracy, since this is a screening context where a missed positive case is the expensive error. On that basis XGBoost was selected as the production model: it reaches the highest recall (0.912) alongside the highest accuracy (0.848) of the four. Random Forest is a close second on ROC-AUC (0.910) with lower recall (0.843), and both linear baselines (Logistic Regression, SVM) trail on accuracy despite competitive AUC. The decision threshold could be lowered further to trade a little precision for additional recall if false negatives needed to be minimized even more aggressively."));
  body.push(table([2520, 1480, 1480, 1300, 1280, 1300],
    [
      ["Model", "CV AUC", "Test AUC", "Accuracy", "Recall", "F1"],
      ["Logistic Regression", "0.881", "0.895", "0.799", "0.824", "0.820"],
      ["Random Forest", "0.883", "0.909", "0.815", "0.843", "0.835"],
      ["XGBoost (selected)", "0.879", "0.905", "0.848", "0.912", "0.869"],
      ["SVM (RBF, calibrated)", "0.883", "0.900", "0.793", "0.863", "0.822"],
    ]));
  body.push(new Paragraph({ spacing: { after: 120 }, children: [] }));
  body.push(p("The selected XGBoost model used 230 trees, max depth 3, a learning rate of 0.047, subsample ratio 0.801, column-subsample ratio 0.574, and L2 regularisation lambda of 2.09 — the shallow trees plus moderate learning rate combination that randomized search found best under cross-validation, consistent with a dataset this size favoring simpler, well-regularized trees over deep ones."));
  body.push(h2("5.2 ROC and confusion matrix"));
  body.push(img("07_roc_xgboost.png", 300, 300, "ROC curve"));
  body.push(caption("Figure 7. ROC curve for the selected XGBoost model on the held-out test set."));
  body.push(img("08_confusion_xgboost.png", 320, 250, "Confusion matrix"));
  body.push(caption("Figure 8. Confusion matrix for the selected XGBoost model."));

  // ----- 6. Experiment tracking -----
  body.push(h1("6. Experiment Tracking with MLflow"));
  body.push(p("Every training run is logged to MLflow under the experiment heart-disease-classification. For each model, the pipeline records the model type and the best hyperparameters, the cross-validated ROC-AUC, the full set of held-out test metrics (accuracy, precision, recall, F1, ROC-AUC), the fitted model itself, and two plot artifacts (ROC curve and confusion matrix). Because all four models log into one experiment, the MLflow UI gives a side-by-side comparison that makes model selection auditable rather than asserted."));
  body.push(p("The tracking store is a local ./mlruns directory, browsable with mlflow ui. The CI workflow uploads this directory as a build artifact, so the experiment history for any commit is preserved alongside the run.", { size: 22 }));
  body.push(bullet("the model type and tuned hyperparameters", "Parameters: "));
  body.push(bullet("cv_roc_auc plus test accuracy, precision, recall, F1, and ROC-AUC", "Metrics: "));
  body.push(bullet("the serialized pipeline, ROC curve, and confusion matrix per run", "Artifacts: "));

  // ----- 7. Packaging -----
  body.push(h1("7. Model Packaging and Reproducibility"));
  body.push(p("The winning pipeline is serialized to models/model.joblib with joblib, and a companion model_metadata.json captures the model type, training timestamp, feature schema, tuned parameters, train/test sizes, and the metrics for every candidate. The API reads this metadata at startup to report which model is live. Because the saved object is the entire pipeline, the preprocessing travels with the model and cannot drift."));
  body.push(p("Reproducibility rests on four supports: a single pinned requirements.txt (mirrored by environment.yml), a fixed random seed of 42 across splitting / CV / tuning, raw data committed in the repository, and a CI job that rebuilds everything from a clean checkout on every push."));

  // ----- 8. CI/CD -----
  body.push(h1("8. CI/CD Pipeline and Automated Testing"));
  body.push(p("Continuous integration runs on GitHub Actions (.github/workflows/ci.yml) on every push and pull request. The first job verifies dataset integrity, lints with ruff, builds the cleaned data, trains and selects the model, then runs the test suite, and uploads the model, EDA figures, and MLflow runs as artifacts. The second job builds the Docker image, runs the container, and executes a smoke test against the live endpoints. Any failing step — a lint violation, a broken test, or a training error — fails the pipeline and surfaces clear logs, satisfying the production-readiness requirement that the pipeline must stop on errors."));
  body.push(h2("8.1 Test suite"));
  body.push(p("The suite contains 22 tests across four files. They cover the data layer (site combination, target binarization, the chol-zero recode, missing-marker handling), the preprocessing pipeline (imputation leaves no NaN, one-hot expansion, unseen-category tolerance), the trained artifact (output schema, probability bounds, a minimum AUC floor), and the API (health, valid prediction, and four input-validation rejections returning HTTP 422)."));
  body.push(table([4680, 4680], [
    ["Test file", "Focus"],
    ["test_data_prep.py", "Loading, cleaning, target binarization"],
    ["test_preprocessing.py", "Imputation, encoding, pipeline fit/predict"],
    ["test_model.py", "Trained artifact and prediction helper"],
    ["test_api.py", "Endpoints and input validation"],
  ]));

  // ----- 9. Containerization -----
  body.push(h1("9. Containerization"));
  body.push(p("The service is packaged with a multi-stage Dockerfile (docker/Dockerfile). The builder stage installs dependencies into a virtual environment; the slim runtime stage copies that environment plus the application code and the trained model, adds libgomp1 for XGBoost and curl for the healthcheck, and runs as a non-root user. A HEALTHCHECK polls /health so the orchestrator knows when the container is ready."));
  body.push(code("docker build -t heart-disease-api:latest -f docker/Dockerfile ."));
  body.push(code("docker run --rm -p 8000:8000 heart-disease-api:latest"));
  body.push(code("bash scripts/smoke_test.sh   # /health, /predict, /metrics"));
  body.push(p("The API exposes POST /predict, which accepts a JSON patient record validated by a pydantic schema (each field range-checked against the UCI codebook) and returns the prediction, probability, confidence, and risk band. GET /health reports liveness and whether the model loaded; GET /metrics exposes Prometheus metrics; /docs serves Swagger UI for interactive testing.", { size: 22 }));

  // ----- 10. Deployment -----
  body.push(h1("10. Production Deployment"));
  body.push(p("The container deploys to Kubernetes via either raw manifests (k8s/) or a Helm chart (k8s/helm/heart-api). The Deployment runs two replicas with CPU and memory requests and limits, plus liveness and readiness probes on /health. A LoadBalancer Service exposes the API, and an optional Ingress routes by host. Prometheus scrape annotations on the pods let an in-cluster Prometheus discover the /metrics endpoint automatically."));
  body.push(code("kubectl apply -f k8s/deployment.yaml -f k8s/service.yaml"));
  body.push(code("# or:  helm install heart k8s/helm/heart-api"));
  body.push(p("On Minikube, building the image into the cluster's Docker daemon and running minikube service heart-api exposes the endpoint locally. Deployment screenshots (pods running, service endpoint, a live /predict response) belong in the screenshots folder of the repository.", { size: 22 }));

  // ----- 11. Monitoring -----
  body.push(h1("11. Monitoring and Logging"));
  body.push(p("The API instruments every request with prometheus_client. Three metric families are exposed: a request counter labelled by endpoint, method, and status; a latency histogram per endpoint; and a counter of predictions by predicted class. A middleware times each request and writes a structured log line to stdout, which is the right place for logs inside a container so a log driver can collect them."));
  body.push(p("docker compose up brings up the API alongside Prometheus and Grafana. Prometheus scrapes /metrics every ten seconds; Grafana auto-provisions the Prometheus datasource and a Heart Disease API dashboard showing request rate, p95 latency, the split of predicted classes, and the 5xx error rate. In an ML context this matters because it surfaces API downtime, latency regressions, and shifts in the prediction mix that can hint at data drift.", { size: 22 }));

  // ----- 12. Repo -----
  body.push(h1("12. Repository and Reproduction"));
  body.push(p("The repository is organized by concern: api/ for the service, src/ for data and model code, tests/ for the suite, data/ for raw and processed data plus the download script, models/ for the saved artifact, docker/ and docker-compose.yml for containers, monitoring/ for Prometheus and Grafana config, k8s/ for manifests and the Helm chart, .github/workflows/ for CI, and reports/ for figures and this document."));
  body.push(new Paragraph({ spacing: { after: 140 }, children: [
    new TextRun({ text: "Code repository: ", bold: true, size: 22 }),
    new ExternalHyperlink({ children: [new TextRun({ text: "https://github.com/guptasaurabh1/heart-disease-mlops", style: "Hyperlink", size: 22 })], link: "https://github.com/guptasaurabh1/heart-disease-mlops" }),
  ] }));
  body.push(p("To reproduce from scratch: clone the repository, create the environment, then run make data, make train, make test, and make serve. Building the cleaned data, training all four models with tuning, and saving the winner takes well under a minute on a laptop.", { size: 22 }));

  // ----- 13. Conclusion -----
  body.push(h1("13. Conclusion"));
  body.push(p("This project delivers a working heart-disease classifier wrapped in the full MLOps lifecycle. The selected XGBoost model reaches a recall of 0.912 and test ROC-AUC of 0.905 on a held-out split, chosen specifically for its recall advantage in this screening context, with Random Forest a close second on ROC-AUC (0.910). More importantly, the surrounding machinery — a reproducible preprocessing pipeline, MLflow tracking, a tested CI/CD workflow, a containerized API, Kubernetes manifests, and Prometheus/Grafana monitoring — turns a notebook model into something that can be retrained, validated, shipped, and watched in production. The natural steps ahead include automated data-drift detection feeding the monitoring stack and a scheduled retraining job triggered when incoming data diverges from the training distribution."));

  return body;
}

Packer.toBuffer(doc).then((buf) => {
  fs.writeFileSync("reports/final_report.docx", buf);
  console.log("Wrote reports/final_report.docx", buf.length, "bytes");
});
