export function renderBreadcrumbs(containerSelector, homeLabel = "Home", homeUrl = "/") {
  const container = document.querySelector(containerSelector);
  if (!container) return;

  // Get the current path and split it
  const pathParts = window.location.pathname.split('/').filter(Boolean);

  // Build breadcrumb HTML
  let html = `<ol class="list-none p-0 inline-flex">`;
  html += `<li class="flex items-center text-blue-500">
    <a href="${homeUrl}" class="text-gray-700">${homeLabel}</a>
    ${pathParts.length ? '<svg class="fill-current w-3 h-3 mx-3" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 512"><path d="M285.476 272.971L91.132 467.314c-9.373 9.373-24.569 9.373-33.941 0l-22.667-22.667c-9.357-9.357-9.375-24.522-.04-33.901L188.505 256 34.484 101.255c-9.335-9.379-9.317-24.544.04-33.901l22.667-22.667c9.373-9.373 24.569-9.373 33.941 0L285.475 239.03c9.373 9.372 9.373 24.568.001 33.941z"/></svg>' : ''}
  </li>`;

  pathParts.forEach((part, idx) => {
    const label = decodeURIComponent(part.replace(/-/g, ' ')).replace(/\b\w/g, l => l.toUpperCase());
    const url = '/' + pathParts.slice(0, idx + 1).join('/');
    const isLast = idx === pathParts.length - 1;
    html += `<li class="flex items-center text-blue-500">
      ${isLast
        ? `<span class="text-gray-600">${label}</span>`
        : `<a href="${url}" class="text-gray-700">${label}</a>
          <svg class="fill-current w-3 h-3 mx-3" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 320 512"><path d="M285.476 272.971L91.132 467.314c-9.373 9.373-24.569 9.373-33.941 0l-22.667-22.667c-9.357-9.357-9.375-24.522-.04-33.901L188.505 256 34.484 101.255c-9.335-9.379-9.317-24.544.04-33.901l22.667-22.667c9.373-9.373 24.569-9.373 33.941 0L285.475 239.03c9.373 9.372 9.373 24.568.001 33.941z"/></svg>`
      }
    </li>`;
  });

  html += `</ol>`;
  container.innerHTML = html;
}
