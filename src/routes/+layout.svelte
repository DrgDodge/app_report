<script lang="ts">
  import '../app.css';
  import '../app.css';
</script>

<svelte:head>
  <meta name="theme-color" content="#ffffff">
  <link rel="manifest" href="data:application/manifest+json;base64,ewogICJuYW1lIjogIlJhcG9ydCBMdWNydSIsCiAgInNob3J0X25hbWUiOiAiUmFwb3J0IiwKICAiZGVzY3JpcHRpb24iOiAiQSB3b3JrIHJlcG9ydCBnZW5lcmF0b3IgYXBwbGljYXRpb24uIiwKICAic3RhcnRfdXJsIjogImh0dHBzOi8vcmVwb3J0Z2VuLmxzZWIudG9wLyIsCiAgImRpc3BsYXkiOiAic3RhbmRhbG9uZSIsCiAgImJhY2tncm91bmRfY29sb3IiOiAiI2ZmZmZmZiIsCiAgInRoZW1lX2NvbG9yIjogIiNmZmZmZmZmIiwKICAiaWNvbnMiOiBbCiAgICB7CiAgICAgICJzcmMiOiAiaHR0cHM6Ly9yZXBvcnRnZW4ubHNlYi50b3AvbG9nby53ZWJwIiwKICAgICAgInNpemVzIjogIjUxMng1MTIiLAogICAgICAidHlwZSI6ICJpbWFnZS93ZWJwIgogICAgfSwKICAgIHsKICAgICAgInNyYyI6ICJodHRwczovL3JlcG9ydGdlbi5sc2ViLnRvcC9mYXZpY29uLnN2ZyIsCiAgICAgICJzaXplcyI6ICJhbnkiLAogICAgICAidHlwZSI6ICJpbWFnZS9zdmcreG1sIgogICAgfQogIF0KfQo=">
</svelte:head>

<div class="min-h-screen flex flex-col bg-gray-100">

  <header class="bg-white shadow-md sticky top-0 z-50">
    <nav class="max-w-7xl mx-auto px-4 py-3">
      <div class="flex justify-between items-center">
        <h1 class="text-2xl font-bold text-gray-900">Generator Rapoarte</h1>
        <div class="flex gap-4">
          <a href="/RaportForm" class="text-lg font-medium text-gray-600 hover:text-gray-900">Raport Form</a>
          <a href="/database" class="text-lg font-medium text-gray-600 hover:text-gray-900">Database</a>
        </div>
      </div>
    </nav>
  </header>

  <main class="flex-grow container mx-auto p-4 sm:p-6 lg:p-8">
    <slot />
  </main>

  <footer class="bg-gray-800 text-white text-center p-4 mt-auto">
    &copy; {new Date().getFullYear()} Toate drepturile rezervate.
  </footer>

</div>
