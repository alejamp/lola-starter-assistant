# Deploy


## Deploying to Railway

1. Create a new Railway project
2. Select Flask as the framework
3. Upload this project to a Github repository
4. Connect Railway to the Github repository
5. Add the following environment variables to Railway:
    - `ASSISTANT_TOKEN` - The token of the assistant you want to use
    - `PROMPTER_URL` - The URL of the Prompter server 
    - `HOST`=0.0.0.0
    - `PORT`=5000
    - `WEBHOOK_URL` - The URL of the webhook, get this from Railway after deploying  e.g. `https://<your-railway-project>.up.railway.app`

