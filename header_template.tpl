<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="description" content="Determine Library book order and inventory">
<meta name="author" content="SZ">
<LINK REL=StyleSheet HREF="http://localhost:8080/static/bootstrap.css" TYPE="text/css" MEDIA=screen>
<LINK REL=StyleSheet HREF="http://localhost:8080/static/bookshelf.css" TYPE="text/css">
<title>{{title or 'No title'}}</title>

<style>
      body {
        padding-top: 60px; /* 60px to make the container go all the way to the bottom of the topbar */
      }

</style>

</head>
<body>
     <div class="navbar navbar-fixed-top">
      <div class="navbar-inner">
        <div class="container">
          <a class="btn btn-navbar" data-toggle="collapse" data-target=".nav-collapse">
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
          </a>
          <a class="brand" href="/books">Know Thy Shelf</a>
          <div class="nav-collapse">
            <ul class="nav">
              <li><a href="/books">Home</a></li>
              <li><a href="/scan">Scan</a></li>
              <li><a href="/new">Add New</a></li>
            </ul>
          </div><!--/.nav-collapse -->
        </div>
      </div>
    </div>
 <div class="container">