# Use the official Nginx image as base
FROM nginx:latest

# Create the sites-available and sites-enabled directories
RUN mkdir -p /etc/nginx/sites-available
RUN mkdir -p /etc/nginx/sites-enabled

# Copy our custom Nginx configuration files into the container
COPY talkaway_be.conf /etc/nginx/sites-available/

# Create symbolic links in sites-enabled
RUN ln -s /etc/nginx/sites-available/talkaway_be.conf /etc/nginx/sites-enabled/

# Remove the default Nginx configuration file
RUN rm /etc/nginx/conf.d/default.conf

# Start Nginx in the background
CMD ["nginx", "-g", "daemon off;"]