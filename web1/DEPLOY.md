# Publish to the Public Web

This project is ready to deploy as a single Python web service.

## Render (recommended)

1. Push this folder to a GitHub repository.
2. In Render, click **New +** -> **Blueprint**.
3. Select your repo. Render will detect `render.yaml`.
4. Deploy.
5. Open the generated URL. The app and API are served together.

## Important note about story storage

Stories are stored in `web1/stories.json`.
On most cloud services, local filesystem writes are ephemeral unless you add a persistent disk/database.
