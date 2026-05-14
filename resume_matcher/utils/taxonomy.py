
'''Skill taxonomy 
Each category maps to seed keywords; any extracted skill is matched here first.'''

TAXONOMY = {
    "Web Development":       ["html", "css", "javascript", "typescript", "react", "vue",
                               "angular", "node", "nextjs", "frontend", "backend", "web",
                               "tailwind", "sass", "rest", "graphql", "api"],
    "Programming Languages": ["python", "java", "c++", "c#", "golang", "rust", "scala",
                               "kotlin", "swift", "ruby", "php", "r", "matlab", "bash"],
    "Data Science & ML":     ["machine learning", "deep learning", "neural network", "nlp",
                               "computer vision", "tensorflow", "pytorch", "scikit", "keras",
                               "pandas", "numpy", "data science", "ai", "ml", "llm",
                               "regression", "classification", "clustering", "statistics"],
    "Data Engineering":      ["spark", "hadoop", "kafka", "airflow", "etl", "pipeline",
                               "data warehouse", "bigquery", "snowflake", "dbt", "databricks"],
    "Cloud & DevOps":        ["aws", "azure", "gcp", "cloud", "docker", "kubernetes", "k8s",
                               "ci/cd", "devops", "terraform", "jenkins", "linux", "ansible",
                               "microservices", "serverless"],
    "Databases":             ["sql", "mysql", "postgresql", "mongodb", "redis", "database",
                               "nosql", "oracle", "sqlite", "elasticsearch", "dynamo"],
    "Control & Automation":  ["control", "pid", "automation", "plc", "scada", "embedded",
                               "firmware", "iot", "robotics", "matlab", "simulink"],
    "Algorithms & CS":       ["algorithm", "data structure", "complexity", "optimization",
                               "graph", "dynamic programming", "sorting", "search"],
    "Version Control & PM":  ["git", "github", "gitlab", "bitbucket", "jira", "agile",
                               "scrum", "kanban", "confluence"],
    "Security":              ["cybersecurity", "penetration", "cryptography", "security",
                               "oauth", "authentication", "ssl", "firewall"],
    "Soft Skills":           ["communication", "leadership", "teamwork", "collaboration",
                               "problem solving", "analytical", "presentation", "management"],
}