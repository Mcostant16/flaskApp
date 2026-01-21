const container = document.querySelector('#example');

const hot = new Handsontable(container, {
  // theme name with obligatory ht-theme-* prefix
  themeName: 'ht-theme-main-dark-auto',
  // other options
  data: [
    ['', 'Tesla', 'Volvo', 'Toyota', 'Ford'],
    ['2019', 10, 11, 12, 13],
    ['2020', 20, 11, 14, 13],
    ['2021', 30, 15, 12, 13],
    ['', '' , '', '',''], 
    ['', '' , '', '',''], 
    ['', '' , '', '',''], 
    ['', '' , '', '','']
  ],
  rowHeaders: true,
  colHeaders: true,
  height: 'auto',
  autoWrapRow: true,
  autoWrapCol: true,
  licenseKey: 'non-commercial-and-evaluation' // for non-commercial use only
});

//Exmple 2
  // Generate a 20x20 empty array
  const rows = 20;
  const cols = 20;
  const data = Array.from({ length: rows }, () => Array(cols).fill(''));

  const container2 = document.getElementById('example2');
  const hot2 = new Handsontable(container2, {
      data: data,
      rowHeaders: true,
      colHeaders: true,
      licenseKey: 'non-commercial-and-evaluation'
  });
