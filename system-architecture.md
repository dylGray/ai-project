graph TD

%% === User Interactions ===
User[User (admin or regular)]

User --> LoginRoute[/login → app.py/]
User --> IndexRoute[/ → app.py/]
User --> ChatRoute[POST /chat → app.py/]
User --> DownloadRoute (ADMINS ONLY) [/download → app.py/]

%% === LOGIN FLOW ===
LoginRoute --> SetSession[session['email']]
SetSession --> CheckAdminLogin[Check if email is in admin_emails]
CheckAdminLogin --> RenderIndexLogin[Render index.html with is_admin flag]

%% === MAIN PAGE ===
IndexRoute --> CheckSession[Read session['email']]
CheckSession --> CheckAdminIndex[Check admin_emails → is_admin]
CheckAdminIndex --> RenderIndex[Render index.html with flags]

%% === CHAT SUBMISSION ===
ChatRoute --> BuildPrompt[Construct messages for GPT]
BuildPrompt --> LoadPromptContext[model.py → build_system_prompt()]
LoadPromptContext --> CallGPT[model.py → get_completion_from_messages()]
CallGPT --> SaveFeedback[utils.py → save_submission()]
SaveFeedback --> FirestoreSave[Save pitch + feedback in Firestore DB]

%% === ADMIN DOWNLOAD ===
DownloadRoute --> FetchSubmissions[utils.py → fetch_all_submissions()]
FetchSubmissions --> FormatCSV[Generate CSV from Firestore data]
FormatCSV --> ReturnDownload[Send CSV file to admin]

%% === ENV CONFIG ===
Environment Variables
EnvVars[ADMIN_EMAILS, SECRET_KEY, OPENAI_API_KEY, FIREBASE_SERVICE_ACCOUNT_JSON]
EnvVars --> app.py
EnvVars --> model.py
EnvVars --> utils.py