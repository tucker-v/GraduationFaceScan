<script>
  import Router, {link} from 'svelte-spa-router';

  import Home from './routes/Home.svelte';
  import SignUp from './routes/SignUp.svelte';
  import Admin from './routes/Admin.svelte';
  import Match from './routes/Match.svelte';
  import Ceremony from './routes/Ceremony.svelte';

  const routes = {
    '/': Home,
    '/signup': SignUp,
    '/admin': Admin,
    '/match': Match,
    '/ceremony': Ceremony,
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