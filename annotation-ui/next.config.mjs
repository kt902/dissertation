/** @type {import('next').NextConfig} */
const nextConfig = {
    webpack: (config, options) => {
      config.module.rules.push({
        test: /\.csv$/,
        use: 'raw-loader'
      });
  
      return config;
    },
  };

export default nextConfig;
