<script lang="ts">
	import '../app.css';

	let { children } = $props();
	let menuOpen = $state(false);
	let browseOpen = $state(false);
	let searchOpen = $state(false);

	function closeMenus() {
		browseOpen = false;
		searchOpen = false;
		menuOpen = false;
	}
</script>

<svelte:head>
	<title>ASPECTT - UK Occupation Information</title>
</svelte:head>

<!-- svelte-ignore a11y_click_events_have_key_events -->
<!-- svelte-ignore a11y_no_static_element_interactions -->
{#if browseOpen || searchOpen}
	<div class="overlay" onclick={closeMenus}></div>
{/if}

<header>
	<div class="container header-inner">
		<a href="/" class="logo" onclick={closeMenus}>
			<span class="logo-mark">A</span>
			<span class="logo-text">
				ASPECTT
				<span class="logo-sub">by the Autonomy Institute</span>
			</span>
		</a>
		<button class="mobile-toggle" onclick={() => (menuOpen = !menuOpen)}>
			{menuOpen ? '\u2715' : '\u2630'}
		</button>
		<nav class:open={menuOpen}>
			<a href="/" onclick={closeMenus}>Home</a>
			<div class="dropdown">
				<button class="nav-link" onclick={() => { browseOpen = !browseOpen; searchOpen = false; }}>
					Browse
					<span class="caret">{browseOpen ? '\u25B4' : '\u25BE'}</span>
				</button>
				{#if browseOpen}
					<div class="dropdown-menu">
						<div class="dropdown-section">
							<span class="dropdown-heading">By group</span>
							<a href="/browse" onclick={closeMenus}>Major groups</a>
							<a href="/browse/job-zones" onclick={closeMenus}>Job zones</a>
							<a href="/browse/interests" onclick={closeMenus}>Interests (RIASEC)</a>
							<a href="/browse/all" onclick={closeMenus}>All occupations</a>
						</div>
						<div class="dropdown-section">
							<span class="dropdown-heading">By descriptor</span>
							<a href="/browse/descriptors/skills" onclick={closeMenus}>Skills</a>
							<a href="/browse/descriptors/abilities" onclick={closeMenus}>Abilities</a>
							<a href="/browse/descriptors/knowledge" onclick={closeMenus}>Knowledge</a>
							<a href="/browse/descriptors/work_activities" onclick={closeMenus}>Work activities</a>
							<a href="/browse/descriptors/work_styles" onclick={closeMenus}>Work styles</a>
						</div>
					</div>
				{/if}
			</div>
			<div class="dropdown">
				<button class="nav-link" onclick={() => { searchOpen = !searchOpen; browseOpen = false; }}>
					Search
					<span class="caret">{searchOpen ? '\u25B4' : '\u25BE'}</span>
				</button>
				{#if searchOpen}
					<div class="dropdown-menu">
						<a href="/search" onclick={closeMenus}>Occupations</a>
						<a href="/search/tasks" onclick={closeMenus}>Job duties</a>
						<a href="/search/technology" onclick={closeMenus}>Technology</a>
						<a href="/search/skills" onclick={closeMenus}>Skills</a>
					</div>
				{/if}
			</div>
			<a href="/compare" onclick={closeMenus}>Compare</a>
			<a href="/crosswalk" onclick={closeMenus}>Crosswalk</a>
			<a href="/api" onclick={closeMenus}>API</a>
			<a href="/about" onclick={closeMenus}>About</a>
		</nav>
	</div>
</header>

<main>
	{@render children()}
</main>

<footer>
	<div class="container footer-inner">
		<div class="footer-content">
			<div class="footer-brand">
				<span class="footer-logo">ASPECTT</span>
				<p>UK occupational information, classified under SOC 2020.</p>
				<p class="footer-data">Data derived from US O*NET v30.2 via an ISCO-08 crosswalk. 412 occupations across 9 major groups.</p>
			</div>
			<div class="footer-nav">
				<span class="footer-nav-heading">Explore</span>
				<a href="/browse">Browse occupations</a>
				<a href="/search">Search</a>
				<a href="/compare">Compare</a>
				<a href="/crosswalk">Crosswalk</a>
			</div>
			<div class="footer-nav">
				<span class="footer-nav-heading">Resources</span>
				<a href="/api">Public API</a>
				<a href="/about">About ASPECTT</a>
				<a href="https://autonomy.work/adu/" target="_blank" rel="noopener">Autonomy Data Unit</a>
				<a href="https://autonomy.work/" target="_blank" rel="noopener">The Autonomy Institute</a>
			</div>
		</div>
		<div class="footer-bottom">
			<p>&copy; {new Date().getFullYear()} The Autonomy Institute</p>
		</div>
	</div>
</footer>

<style>
	header {
		background: var(--color-primary);
		color: white;
		padding: 0;
		position: sticky;
		top: 0;
		z-index: 100;
		border-bottom: 2px solid var(--color-accent-bright);
	}

	.header-inner {
		display: flex;
		align-items: center;
		justify-content: space-between;
		height: 68px;
	}

	.logo {
		display: flex;
		align-items: center;
		gap: 0.65rem;
		color: white;
		flex-shrink: 0;
	}

	.logo:hover {
		text-decoration: none;
	}

	.logo:hover .logo-mark {
		background: var(--color-accent-light);
	}

	.logo-mark {
		display: flex;
		align-items: center;
		justify-content: center;
		width: 38px;
		height: 38px;
		background: var(--color-accent-bright);
		border: none;
		border-radius: 9px;
		font-size: 1.2rem;
		font-weight: 800;
		letter-spacing: 0;
		color: white;
		transition: background 0.2s;
	}

	.logo-text {
		display: flex;
		flex-direction: column;
		font-size: 1.25rem;
		font-weight: 700;
		letter-spacing: 0.12em;
		line-height: 1.15;
	}

	.logo-sub {
		font-size: 0.6rem;
		font-weight: 400;
		letter-spacing: 0.01em;
		opacity: 0.55;
	}

	nav {
		display: flex;
		align-items: center;
		gap: 0.125rem;
	}

	nav > a, .nav-link {
		color: rgba(255, 255, 255, 0.65);
		font-size: 0.8125rem;
		font-weight: 450;
		transition: color var(--transition);
		padding: 0.375rem 0.625rem;
		border-radius: 4px;
		background: none;
		border: none;
		cursor: pointer;
		white-space: nowrap;
		font-family: var(--font);
		letter-spacing: 0.01em;
	}

	nav > a:hover, .nav-link:hover {
		color: white;
		text-decoration: none;
	}

	.caret {
		font-size: 0.6rem;
		margin-left: 0.125rem;
		opacity: 0.6;
	}

	.dropdown {
		position: relative;
	}

	.dropdown-menu {
		position: absolute;
		top: calc(100% + 0.75rem);
		left: 0;
		background: var(--color-surface);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-lg);
		box-shadow: var(--shadow-lg);
		min-width: 180px;
		padding: 0.5rem 0;
		z-index: 200;
		display: flex;
		gap: 0;
		animation: dropdown-in 0.15s ease-out;
	}

	@keyframes dropdown-in {
		from { opacity: 0; transform: translateY(-4px); }
		to { opacity: 1; transform: translateY(0); }
	}

	.dropdown-section {
		display: flex;
		flex-direction: column;
		padding: 0 0.25rem;
		min-width: 170px;
	}

	.dropdown-section + .dropdown-section {
		border-left: 1px solid var(--color-border);
	}

	.dropdown-heading {
		font-size: 0.65rem;
		font-weight: 600;
		text-transform: uppercase;
		letter-spacing: 0.08em;
		color: var(--color-text-secondary);
		padding: 0.5rem 0.875rem 0.375rem;
	}

	.dropdown-menu a {
		display: block;
		padding: 0.375rem 0.875rem;
		font-size: 0.8125rem;
		color: var(--color-text);
		border-radius: 4px;
		margin: 0 0.25rem;
		font-weight: 450;
	}

	.dropdown-menu a:hover {
		background: var(--color-bg);
		text-decoration: none;
		color: var(--color-text);
	}

	.overlay {
		position: fixed;
		inset: 0;
		z-index: 50;
	}

	.mobile-toggle {
		display: none;
		background: none;
		border: none;
		color: white;
		font-size: 1.25rem;
		cursor: pointer;
		padding: 0.25rem;
	}

	main {
		min-height: calc(100vh - 180px);
		padding: 2.5rem 0;
	}

	footer {
		background: var(--color-primary);
		color: rgba(255, 255, 255, 0.5);
		padding: 3rem 0 1.5rem;
		font-size: 0.8125rem;
		line-height: 1.7;
		margin-top: auto;
	}

	footer a {
		color: rgba(255, 255, 255, 0.65);
		transition: color var(--transition);
	}

	footer a:hover {
		color: var(--color-accent-bright);
		text-decoration: none;
	}

	.footer-content {
		display: grid;
		grid-template-columns: 2fr 1fr 1fr;
		gap: 3rem;
		padding-bottom: 2rem;
		border-bottom: 1px solid rgba(255, 255, 255, 0.06);
	}

	.footer-brand {
		display: flex;
		flex-direction: column;
		gap: 0.375rem;
	}

	.footer-data {
		margin-top: 0.375rem;
		font-size: 0.75rem;
		opacity: 0.7;
	}

	.footer-logo {
		font-weight: 700;
		font-size: 0.9rem;
		letter-spacing: 0.12em;
		color: rgba(255, 255, 255, 0.85);
	}

	.footer-nav {
		display: flex;
		flex-direction: column;
		gap: 0.375rem;
	}

	.footer-nav-heading {
		font-size: 0.6875rem;
		font-weight: 600;
		text-transform: uppercase;
		letter-spacing: 0.1em;
		color: rgba(255, 255, 255, 0.35);
		margin-bottom: 0.25rem;
	}

	.footer-bottom {
		padding-top: 1.25rem;
		text-align: center;
		font-size: 0.75rem;
		opacity: 0.5;
	}

	@media (max-width: 768px) {
		.mobile-toggle {
			display: block;
		}

		nav {
			display: none;
			position: absolute;
			top: 100%;
			left: 0;
			right: 0;
			background: var(--color-primary);
			flex-direction: column;
			padding: 0.5rem 1.25rem 1rem;
			align-items: stretch;
			gap: 0;
			border-top: 1px solid rgba(255, 255, 255, 0.06);
		}

		nav.open {
			display: flex;
		}

		.dropdown-menu {
			position: static;
			box-shadow: none;
			border: none;
			background: rgba(255, 255, 255, 0.04);
			border-radius: 4px;
			margin: 0.25rem 0;
			flex-direction: column;
		}

		.dropdown-section + .dropdown-section {
			border-left: none;
			border-top: 1px solid rgba(255, 255, 255, 0.06);
		}

		.dropdown-heading {
			color: rgba(255, 255, 255, 0.4);
		}

		.dropdown-menu a {
			color: rgba(255, 255, 255, 0.75);
		}

		.dropdown-menu a:hover {
			background: rgba(255, 255, 255, 0.06);
			color: white;
		}

		.footer-content {
			grid-template-columns: 1fr;
			gap: 1.75rem;
		}

		.footer-nav {
			gap: 0.25rem;
		}
	}
</style>
