<script lang="ts">
	import '../app.css';

	let { children } = $props();
</script>

<svelte:head>
	<title>ASPECTT - UK Occupation Information</title>
</svelte:head>

<header>
	<div class="container header-inner">
		<a href="/" class="logo">
			<span class="logo-mark">A</span>SPECTT
		</a>
		<nav>
			<a href="/">Home</a>
			<a href="/browse">Browse</a>
			<a href="/search">Search</a>
			<a href="/api">API</a>
		</nav>
	</div>
</header>

<main>
	{@render children()}
</main>

<footer>
	<div class="container footer-inner">
		<p>ASPECTT &mdash; UK Occupational Information based on SOC 2020</p>
		<p class="footer-sub">Data derived from US O*NET v30.2 via ISCO-08 crosswalk</p>
	</div>
</footer>

<style>
	header {
		background: var(--color-primary);
		color: white;
		padding: 0.75rem 0;
		box-shadow: var(--shadow-md);
		position: sticky;
		top: 0;
		z-index: 100;
	}

	.header-inner {
		display: flex;
		align-items: center;
		justify-content: space-between;
	}

	.logo {
		font-size: 1.5rem;
		font-weight: 800;
		color: white;
		letter-spacing: 2px;
	}

	.logo:hover {
		text-decoration: none;
	}

	.logo-mark {
		display: inline-flex;
		align-items: center;
		justify-content: center;
		width: 2rem;
		height: 2rem;
		background: var(--color-accent);
		border-radius: 6px;
		margin-right: 0.25rem;
		font-size: 1.25rem;
	}

	nav {
		display: flex;
		gap: 1.5rem;
	}

	nav a {
		color: rgba(255, 255, 255, 0.85);
		font-size: 0.9rem;
		font-weight: 500;
		transition: color 0.15s;
	}

	nav a:hover {
		color: white;
		text-decoration: none;
	}

	main {
		min-height: calc(100vh - 160px);
		padding: 2rem 0;
	}

	footer {
		background: var(--color-primary);
		color: rgba(255, 255, 255, 0.7);
		padding: 1.5rem 0;
		text-align: center;
	}

	.footer-sub {
		font-size: 0.8rem;
		margin-top: 0.25rem;
		opacity: 0.6;
	}
</style>
