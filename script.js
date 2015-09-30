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
