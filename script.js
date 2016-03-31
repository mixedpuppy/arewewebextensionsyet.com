/*
var bugzilla = bz.createClient();

bugzilla.searchBugs({
  product: 'Toolkit',
  component: 'WebExtensions',
  bug_status: ['UNCONFIRMED', 'NEW', 'ASSIGNED', 'REOPENED'],
}, function(error, bugs) {
  if (!error) {
    document.getElementById('open').innerHTML = bugs.length;
  }
});

bugzilla.searchBugs({
  product: 'Toolkit',
  component: 'WebExtensions',
  bug_status: ['RESOLVED', 'VERIFIED', 'CLOSED'],
}, function(error, bugs) {
  if (!error) {
    document.getElementById('closed').innerHTML = bugs.length;
  }
});
*/

function count() {
  var count = 0;
  for (let api of document.getElementsByClassName("api-group")) {
    if (api.style.display === "block") {
      count++;
    };
  }
  document.getElementById("count").innerHTML = count;
}

for (let element of document.getElementsByClassName("filter")) {
  element.addEventListener("click", function(e) {
    e.preventDefault();
    for (let api of document.getElementsByClassName("api-group")) {
      keep = false;

      function find(elements, named) {
        for (let span of elements.getElementsByTagName("span")) {
          if (span.innerHTML === named) {
            return true;
          }
        }
        return false;
      }

      if (this.id === "desktop-only") {
        keep = find(api, "desktop");
      }

      if (this.id === "android-only") {
        keep = find(api, "android");
      }

      if (this.id === "complete-only" || this.id === "complete-partial-only") {
        keep = find(api, "complete");
      }

      if (!keep && (this.id === "partial-only" || this.id === "complete-partial-only")) {
        keep = find(api, "partial");
      }

      if (this.id === "reset") {
        keep = true;
      }

      if (keep) {
        api.style.display = 'block';
      } else {
        api.style.display = 'none';
      }
    }

    count();
  })
}

count();
