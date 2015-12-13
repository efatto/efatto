function hid() {
            if ( document.getElementById('myid').innerHTML == '1' ) {
             document.getElementById('first_page').style.display = 'none';
             document.getElementById('other_pages').style.display = 'inline';
            }
            else {
             document.getElementById('first_page').style.display = 'inline';
             document.getElementById('other_pages').style.display = 'none';
            }
           }