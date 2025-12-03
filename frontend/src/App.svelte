<script>
  import Router, {link} from 'svelte-spa-router';

  import Home from './routes/Home.svelte';
  import SignUp from './routes/SignUp.svelte';
  import Admin from './routes/Admin.svelte';
  import Match from './routes/Match.svelte';
  import Ceremony from './routes/Ceremony.svelte';
  import Login from './routes/Login.svelte';
  import AdminProfile from './routes/AdminProfile.svelte';
  import Reports from './routes/Reports.svelte';

  const routes = {
    '/': Home,
    '/signup': SignUp,
    '/admin': Admin,
    '/match': Match,
    '/ceremony': Ceremony,
    '/login': Login,
    '/admin/profile': AdminProfile,
    '/reports': Reports
  };
</script>

<header>
  <a href="/" use:link>
    <h1>GFS Frontend</h1>
  </a>
</header>

<main>
  <Router {routes} />
</main>

<style>
  header {
    text-align: center;
    margin-bottom: 1.5rem;
  }

  header a {
    text-decoration: none;
    color: inherit;
  }

  main {
    width: 100%;
  }
</style>
