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
			<span class="logo-mark">A</span>SPECTT
		</a>
		<button class="mobile-toggle" onclick={() => (menuOpen = !menuOpen)}>
			{menuOpen ? '\u2715' : '\u2630'}
		</button>
		<nav class:open={menuOpen}>
			<a href="/" onclick={closeMenus}>Home</a>
			<div class="dropdown">
				<button class="nav-link" onclick={() => { browseOpen = !browseOpen; searchOpen = false; }}>
					Find Occupations
					<span class="caret">{browseOpen ? '\u25B4' : '\u25BE'}</span>
				</button>
				{#if browseOpen}
					<div class="dropdown-menu">
						<div class="dropdown-section">
							<span class="dropdown-heading">Browse by</span>
							<a href="/browse" onclick={closeMenus}>Major Groups</a>
							<a href="/browse/job-zones" onclick={closeMenus}>Job Zones</a>
							<a href="/browse/interests" onclick={closeMenus}>Interests (RIASEC)</a>
							<a href="/browse/all" onclick={closeMenus}>All Occupations</a>
						</div>
						<div class="dropdown-section">
							<span class="dropdown-heading">By Descriptor</span>
							<a href="/browse/descriptors/skills" onclick={closeMenus}>Skills</a>
							<a href="/browse/descriptors/abilities" onclick={closeMenus}>Abilities</a>
							<a href="/browse/descriptors/knowledge" onclick={closeMenus}>Knowledge</a>
							<a href="/browse/descriptors/work_activities" onclick={closeMenus}>Work Activities</a>
							<a href="/browse/descriptors/work_styles" onclick={closeMenus}>Work Styles</a>
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
						<a href="/search" onclick={closeMenus}>Occupation Search</a>
						<a href="/search/tasks" onclick={closeMenus}>Job Duties Search</a>
						<a href="/search/technology" onclick={closeMenus}>Technology Skills</a>
						<a href="/search/skills" onclick={closeMenus}>Skills Search</a>
					</div>
				{/if}
			</div>
			<a href="/compare" onclick={closeMenus}>Compare</a>
			<a href="/crosswalk" onclick={closeMenus}>Crosswalk</a>
			<a href="/api" onclick={closeMenus}>API</a>
		</nav>
	</div>
</header>

<main>
	{@render children()}
</main>

<footer>
	<div class="container footer-inner">
		<p>ASPECTT &mdash; UK Occupational Information based on SOC 2020</p>
		<p class="footer-sub">Data derived from US O*NET v30.2 via ISCO-08 crosswalk. 412 occupations across 9 major groups.</p>
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
		flex-shrink: 0;
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
		align-items: center;
		gap: 0.25rem;
	}

	nav > a, .nav-link {
		color: rgba(255, 255, 255, 0.85);
		font-size: 0.875rem;
		font-weight: 500;
		transition: color 0.15s;
		padding: 0.4rem 0.65rem;
		border-radius: 6px;
		background: none;
		border: none;
		cursor: pointer;
		white-space: nowrap;
	}

	nav > a:hover, .nav-link:hover {
		color: white;
		background: rgba(255, 255, 255, 0.1);
		text-decoration: none;
	}

	.caret {
		font-size: 0.65rem;
		margin-left: 0.15rem;
	}

	.dropdown {
		position: relative;
	}

	.dropdown-menu {
		position: absolute;
		top: calc(100% + 0.5rem);
		left: 0;
		background: var(--color-surface);
		border-radius: var(--radius);
		box-shadow: var(--shadow-md), 0 8px 24px rgba(0,0,0,0.12);
		min-width: 200px;
		padding: 0.5rem 0;
		z-index: 200;
		display: flex;
		gap: 0;
	}

	.dropdown-section {
		display: flex;
		flex-direction: column;
		padding: 0 0.25rem;
		min-width: 180px;
	}

	.dropdown-section + .dropdown-section {
		border-left: 1px solid var(--color-border);
	}

	.dropdown-heading {
		font-size: 0.7rem;
		font-weight: 700;
		text-transform: uppercase;
		letter-spacing: 0.05em;
		color: var(--color-text-secondary);
		padding: 0.5rem 1rem 0.25rem;
	}

	.dropdown-menu a {
		display: block;
		padding: 0.4rem 1rem;
		font-size: 0.85rem;
		color: var(--color-text);
		border-radius: 4px;
		margin: 0 0.25rem;
	}

	.dropdown-menu a:hover {
		background: var(--color-bg);
		text-decoration: none;
		color: var(--color-accent);
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
		font-size: 1.5rem;
		cursor: pointer;
		padding: 0.25rem;
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
			padding: 0.5rem 1rem 1rem;
			align-items: stretch;
			gap: 0;
		}

		nav.open {
			display: flex;
		}

		.dropdown-menu {
			position: static;
			box-shadow: none;
			background: rgba(255,255,255,0.05);
			border-radius: 4px;
			margin: 0.25rem 0;
			flex-direction: column;
		}

		.dropdown-section + .dropdown-section {
			border-left: none;
			border-top: 1px solid rgba(255,255,255,0.1);
		}

		.dropdown-heading {
			color: rgba(255,255,255,0.5);
		}

		.dropdown-menu a {
			color: rgba(255,255,255,0.85);
		}

		.dropdown-menu a:hover {
			background: rgba(255,255,255,0.1);
			color: white;
		}
	}
</style>
