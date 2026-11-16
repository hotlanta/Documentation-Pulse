const C="dp-v2",SHELL=["./","index.html","manifest.webmanifest","icon.svg","icon-192.png","icon-512.png"];
self.addEventListener("install",e=>e.waitUntil(caches.open(C).then(c=>c.addAll(SHELL))));
self.addEventListener("fetch",e=>{
  if(e.request.method!=="GET")return;
  e.respondWith(fetch(e.request).then(r=>{const k=r.clone();caches.open(C).then(c=>c.put(e.request,k));return r})
    .catch(()=>caches.match(e.request)));
});
