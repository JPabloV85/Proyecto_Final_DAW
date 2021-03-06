window.onload = function() {
  window.ui = SwaggerUIBundle({
    url: "../../static/swagger.json",
    dom_id: '#swagger-ui',
    deepLinking: true,
    presets: [
      SwaggerUIBundle.presets.apis,
      SwaggerUIStandalonePreset
    ],
    plugins: [
      SwaggerUIBundle.plugins.DownloadUrl,
      HideCurlPlugin,
      HideTopbarPlugin
    ],
    layout: "StandaloneLayout"
  });
};
