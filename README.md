<h1 align="center">Spotify MusiVault🎵🎶🎛️🎼💾💽🗄️🗃️</h1>

<p align="center"><i>✨ Coded with help from GPT4 ✨</i></p>

This project is a Spotify Data Sync and Backup Tool that allows users to authenticate and sync their Spotify music data, including liked songs, playlists, and metadata, using a Flask backend with Spotipy. Data is stored locally in an SQLite database and backed up to Google Drive for security. The tool features a React-based user interface for easy interaction and is containerized with Docker for straightforward deployment and maintenance. Hosted on GitHub, it offers a robust solution for users to manage and safeguard their Spotify data.

> [!NOTE]
> *Based on my prior attempt at this project: [Spotify Backup](https://github.com/romano-w/spotify_backup)*

---
## GPT4 Generated Project Guideline

Based on selected tools and preferences, here's a refined guideline for your Spotify data retrieval and storage project:

### Required Tools

1. **Backend**: Flask (Python)
2. **API Communication**: Spotipy (fallback: Requests)
3. **Frontend**: React (JavaScript)
4. **Authentication**: OAuth
5. **Local Database**: SQLite
6. **Cloud Backup**: Google Drive
7. **Containerization**: Docker
8. **Version Control**: GitHub
9. **Package Manager**: Poetry

### Project Structure

1. **Flask Backend**:
   - Handles OAuth authentication with Spotify.
   - Manages API requests to Spotify using Spotipy.
   - Processes and stores retrieved data in SQLite.

2. **React Frontend**:
   - User interface for initiating authentication and displaying sync status.

3. **SQLite Database**:
   - Local storage of user's Spotify data.

4. **Google Drive Integration**:
   - Cloud backup for the SQLite database.

### Development Roadmap

#### Phase 1: Setup and Initial Backend

1. **Environment Setup**:
   - Setup Python, Node.js, and necessary development tools.
   - Initialize Flask app and React app in your GitHub repository.

2. **Spotify Developer Registration**:
   - Register your app with Spotify to obtain client ID and client secret.

3. **Flask App for Authentication**:
   - Implement OAuth flow in Flask to authenticate with Spotify.
   - Test authentication flow to ensure it's working correctly.

4. **Integrate Spotipy**:
   - Use Spotipy to connect to Spotify API and test basic data retrieval (like fetching user profile).

#### Phase 2: Data Retrieval and Local Storage

5. **Expand Data Retrieval**:
   - Retrieve liked songs, playlists, datetimes, and metadata using Spotipy.

6. **SQLite Integration**:
   - Set up SQLite database.
   - Define data models and schemas corresponding to the Spotify data.

7. **Data Storage Logic**:
   - Implement logic to store and update Spotify data in SQLite.
   - Ensure proper data processing and error handling.

8. **Local Testing**:
   - Test the complete flow from authentication to data retrieval and storage.

#### Phase 3: Frontend Development

9. **React Setup**:
   - Develop basic frontend using React.
   - Implement UI for user login and initiating data sync.

10. **Frontend-Backend Integration**:
    - Connect React app with Flask backend.
    - Test end-to-end flow with the frontend.

#### Phase 4: Cloud Backup and Finalization

11. **Google Drive Integration**:
    - Implement functionality to back up SQLite database to Google Drive.
    - Test backup and restore processes.

12. **Containerization with Docker**:
    - Create a Dockerfile for your application.
    - Test running your application in a Docker container.

13. **Final Testing and Refinement**:
    - Conduct thorough testing of the entire application.
    - Refine features and fix any bugs.

14. **Documentation**:
    - Document the setup process, usage instructions, and any important details about your application.

#### Phase 5: Deployment (Optional)

- If I decide to deploy this application publicly, consider setting up a cloud server (like AWS EC2) and deploying the Docker container there.

---

## ⚡ Quick Start

### Prerequisites

### Installation

## ✨Usage
