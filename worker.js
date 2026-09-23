// Edge entrypoint: redirect www to the apex domain, serve static assets otherwise.
//
// Both https://dodgecityfootball.com and https://www.dodgecityfootball.com
// should be attached to this Worker as custom domains. Any request arriving
// on www gets a 301 to the same path + query on the apex; everything else
// falls through to Static Assets.
export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    if (url.hostname === "www.dodgecityfootball.com") {
      url.hostname = "dodgecityfootball.com";
      return Response.redirect(url.toString(), 301);
    }
    return env.ASSETS.fetch(request);
  },
};
