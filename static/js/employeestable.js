 //Example 3 - Flask + Jinja + JS
 //const tableData = {{ table_data | tojson }};

console.log('example:', document.getElementById('tableExample'));
   // Generate a 20x20 empty array


document.addEventListener('DOMContentLoaded', () => {
  const container3 = document.getElementById('tableExample');

 let hot3; 

if (!container3) {
    console.error('Container element not found!');
} else {
    console.log('Container element found:', window.employeesData);
  hot3 =       
  new Handsontable(container3, {
    height: 400,
    data: window.employeesData || [],
    colHeaders: ['ID', 'Name', 'Role'],
    columns: [
      { data: 'id', type: 'numeric', readOnly: true },
      { data: 'name', type: 'text' },
      { data: 'role', type: 'text' },
    ],

    rowHeaders: true,
    colHeaders: true,
    licenseKey: 'non-commercial-and-evaluation'
  });

    window.employeesHot = hot3;
}

  const rows2 = 20;
  const cols2 = 20;
  const data22 = Array.from({ length: rows2 }, () => Array(cols2).fill(''));

  
  const container4 = document.getElementById('userSubmissions');
  let hot4;

if (!container4) {
    console.error('Container element not found!');
} else {
    console.log('Container element found:', window.employeesData);
   hot4 =       
  new Handsontable(container4, {
     data: data22,
      rowHeaders: true,
      colHeaders: true,
      licenseKey: 'non-commercial-and-evaluation'
  });

    window.employeesHot = hot4;
}

// Toast helpers
  const successToast = () => new bootstrap.Toast(document.getElementById('saveToast')).show();
  const errorToast = (msg) => {
    const body = document.getElementById('errorToastBody');
    if (body) body.textContent = msg || 'Error saving data.';
    new bootstrap.Toast(document.getElementById('errorToast')).show();
  };

  // Optional: CSRF token from meta tag (if using Flask-WTF/CSRFProtect)
  // <meta name="csrf-token" content="{{ csrf_token() }}">
  const csrfToken = document.querySelector('meta[name="csrf-token"]')?.getAttribute('content');

  const saveBtn = document.getElementById('saveBtn');
  if (!saveBtn) return;

  saveBtn.addEventListener('click', async () => {
    try {
      // Disable during save
      saveBtn.disabled = true;
      saveBtn.textContent = 'Saving…';

      // Get data from Handsontable
      const payload = hot4.getSourceData(); // array of objects [{id, name, role}, ...]
      console.log('Payload to save:', payload);

      const res = await fetch('/api/employees/save', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(csrfToken ? { 'X-CSRFToken': csrfToken } : {}) // if CSRF enabled
        },
        body: JSON.stringify(payload),
        credentials: 'same-origin' // send cookies if needed
      });

      const result = await res.json().catch(() => ({}));

      if (res.ok) {
        successToast();
        // Optional: refresh data from server or update IDs for new rows
        // await reloadData();
      } else {
        errorToast(result.error || `Save failed (HTTP ${res.status})`);
      }
    } catch (err) {
      console.error(err);
      errorToast(err.message || 'Network error while saving.');
    } finally {
      saveBtn.disabled = false;
      saveBtn.textContent = 'Save Changes';
    }
  });

  // Example function to reload data from server if you want
  async function reloadData() {
    const res = await fetch('/api/employees');
    const data = await res.json();
    hot.loadData(data);
    hot.render();
  }
});   
  // If you prefer to load data via API instead of inline:
  // reloadData();






const toast = new bootstrap.Toast(document.getElementById('saveToast'));
toast.show();
