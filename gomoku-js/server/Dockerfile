# Use the official Node.js image as the base image
FROM node:22

# Create and change to the app directory
WORKDIR /usr/src/app

# Copy the rest of the application code
COPY . .

RUN npm install -g typescript

RUN npm install && tsc

# Expose the port the app runs on
EXPOSE 3000

# Define the command to run the app
CMD ["node", "src/index.js"]
