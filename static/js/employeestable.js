 //Example 3 - Flask + Jinja + JS
 // const tableData = {{ table_data | tojson }};

console.log('example:', document.getElementById('tableExample'));
   // Generate a 20x20 empty array
  const rows2 = 20;
  const cols2 = 20;
  const data22 = Array.from({ length: rows2 }, () => Array(cols2).fill(''));

  
  const container3 = document.getElementById('tableExample');

if (!container3) {
    console.error('Container element not found!');
} else {
  const hot3 =       
  new Handsontable(container3, {
    data: data22,
    rowHeaders: true,
    colHeaders: true,
    licenseKey: 'non-commercial-and-evaluation'
  });
}

