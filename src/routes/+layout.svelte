<script lang="ts">
  import '../app.css';
  // 1. Asigură-te că imporți fișierul CSS principal al Tailwind
  // (Numele poate fi app.pcss, app.css, tailwind.css, etc.,
  // în funcție de cum l-ai configurat)
  import '../app.css';
</script>

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
