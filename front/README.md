# AWSomeShop Frontend

This directory contains the frontend applications for AWSomeShop.

## Structure

- `personal/` - Employee portal (员工端)
- `manage/` - Management portal (管理端)
- `static/` - Build output directory

## Prerequisites

- Node.js 14+ and npm
- Vue CLI 5.x

## Installation

### Install Vue CLI globally (if not already installed)
```bash
npm install -g @vue/cli
```

### Install dependencies for both applications

```bash
# Install personal portal dependencies
cd personal
npm install

# Install management portal dependencies
cd ../manage
npm install
```

## Development

### Run personal portal in development mode
```bash
cd personal
npm run serve
```
Access at: http://localhost:8080

### Run management portal in development mode
```bash
cd manage
npm run serve
```
Access at: http://localhost:8081

## Build for Production

### Build personal portal
```bash
cd personal
npm run build
```
Output: `../static/personal/`

### Build management portal
```bash
cd manage
npm run build
```
Output: `../static/manage/`

### Build both applications
```bash
# From the front directory
cd personal && npm run build && cd ../manage && npm run build
```

## Features

### Personal Portal (员工端)
- User authentication
- Product browsing with search and filtering
- Shopping cart management
- Order placement and history
- Points balance and transaction history
- Profile and address management

### Management Portal (管理端)
- User management (CRUD operations)
- Product management with image upload
- Category management (tree structure)
- Points granting (single and batch)
- Admin operation logs

## API Integration

Both applications are configured to proxy API requests to the backend server:
- Development: Proxies to `http://localhost:8000`
- Production: Serves from the same origin as the backend

## Technology Stack

- Vue 2.6
- Element UI 2.15
- Vuex 3.6
- Vue Router 3.5
- Axios 0.27

## Notes

- The applications use session-based authentication
- CSRF tokens are automatically handled by the request interceptor
- All API responses follow a unified format
- Error handling is centralized in the Axios interceptor
