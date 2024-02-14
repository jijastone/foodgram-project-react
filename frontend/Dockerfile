FROM node:13.12.0-alpine as build
WORKDIR /app
COPY package*.json ./
RUN npm cache clean --force
RUN npm install
RUN npm cache clean --force
COPY . ./
RUN npm run build
CMD cp -r build result_build