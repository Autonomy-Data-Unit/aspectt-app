<script lang="ts">
	import { searchOccupations, getStats, type Occupation } from '$lib/api/client';
	import { goto } from '$app/navigation';

	let query = $state('');
	let results = $state<Occupation[]>([]);
	let total = $state(0);
	let stats = $state<{ total_occupations: number } | null>(null);
	let searching = $state(false);
	let debounceTimer: ReturnType<typeof setTimeout>;

	$effect(() => {
		getStats().then((s) => (stats = s));
	});

	function handleInput() {
		clearTimeout(debounceTimer);
		if (query.trim().length < 1) {
			results = [];
			total = 0;
			return;
		}
		searching = true;
		debounceTimer = setTimeout(async () => {
			const data = await searchOccupations(query, 12);
			results = data.occupations;
			total = data.total;
			searching = false;
		}, 200);
	}

	function handleSubmit(e: Event) {
		e.preventDefault();
		if (query.trim()) goto(`/search?q=${encodeURIComponent(query.trim())}`);
	}
</script>

<div class="hero">
	<div class="container">
		<h1>ASPECTT</h1>
		<p class="subtitle">UK Occupation Information System</p>
		<p class="desc">
			Explore detailed data on {stats?.total_occupations ?? '...'} UK occupations including
			skills, abilities, knowledge, tasks, and more — based on UK SOC 2020.
		</p>

		<form class="search-box" onsubmit={handleSubmit}>
			<input
				class="search-input search-hero"
				type="text"
				placeholder="Search occupations by title or SOC code..."
				bind:value={query}
				oninput={handleInput}
			/>
			<button class="btn btn-primary search-btn" type="submit">Search</button>
		</form>

		{#if results.length > 0}
			<div class="results-dropdown">
				{#each results as occ}
					<a class="result-item" href="/occupation/{occ.uk_soc_2020}">
						<span class="result-code">{occ.uk_soc_2020}</span>
						<span class="result-title">{occ.title}</span>
					</a>
				{/each}
				{#if total > 12}
					<a class="result-more" href="/search?q={encodeURIComponent(query)}">
						View all {total} results →
					</a>
				{/if}
			</div>
		{/if}
	</div>
</div>

<div class="container">
	<div class="features">
		<a href="/browse" class="feature-card">
			<h3>Browse Occupations</h3>
			<p>Explore all UK SOC 2020 occupations by major group, job zone, or category.</p>
		</a>
		<a href="/search" class="feature-card">
			<h3>Search & Compare</h3>
			<p>Find occupations by keyword, SOC code, or skill requirements.</p>
		</a>
		<a href="/api" class="feature-card">
			<h3>Public API</h3>
			<p>Access occupation data programmatically via our REST API.</p>
		</a>
	</div>

	<div class="card">
		<h2>Data Categories</h2>
		<div class="categories">
			<span class="cat-tag">Abilities</span>
			<span class="cat-tag">Skills</span>
			<span class="cat-tag">Knowledge</span>
			<span class="cat-tag">Work Activities</span>
			<span class="cat-tag">Work Context</span>
			<span class="cat-tag">Work Styles</span>
			<span class="cat-tag">Interests</span>
			<span class="cat-tag">Work Values</span>
			<span class="cat-tag">Tasks</span>
			<span class="cat-tag">Technology Skills</span>
			<span class="cat-tag">Education</span>
			<span class="cat-tag">Related Occupations</span>
		</div>
	</div>
</div>

<style>
	.hero {
		background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-primary-light) 100%);
		color: white;
		padding: 3rem 0 4rem;
		margin: -2rem 0 2rem;
		text-align: center;
		position: relative;
	}

	h1 {
		font-size: 3rem;
		letter-spacing: 6px;
		font-weight: 800;
		margin-bottom: 0.25rem;
	}

	.subtitle {
		font-size: 1.2rem;
		opacity: 0.85;
		margin-bottom: 0.75rem;
	}

	.desc {
		max-width: 600px;
		margin: 0 auto 1.5rem;
		opacity: 0.75;
		font-size: 0.95rem;
	}

	.search-box {
		display: flex;
		gap: 0.5rem;
		max-width: 600px;
		margin: 0 auto;
		position: relative;
	}

	.search-hero {
		flex: 1;
		border: none;
		box-shadow: var(--shadow-md);
	}

	.search-btn {
		padding: 0.75rem 1.5rem;
		font-size: 1rem;
	}

	.results-dropdown {
		position: absolute;
		top: 100%;
		left: 50%;
		transform: translateX(-50%);
		width: 100%;
		max-width: 600px;
		background: white;
		border-radius: var(--radius);
		box-shadow: var(--shadow-md);
		z-index: 50;
		margin-top: 0.25rem;
		overflow: hidden;
	}

	.result-item {
		display: flex;
		gap: 0.75rem;
		padding: 0.6rem 1rem;
		color: var(--color-text);
		transition: background 0.1s;
	}

	.result-item:hover {
		background: var(--color-bg);
		text-decoration: none;
	}

	.result-code {
		font-family: monospace;
		font-weight: 600;
		color: var(--color-accent);
		flex: 0 0 50px;
	}

	.result-title {
		flex: 1;
		text-align: left;
	}

	.result-more {
		display: block;
		padding: 0.5rem 1rem;
		text-align: center;
		background: var(--color-bg);
		font-size: 0.875rem;
		font-weight: 500;
	}

	.features {
		display: grid;
		grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
		gap: 1rem;
		margin-bottom: 1.5rem;
	}

	.feature-card {
		background: var(--color-surface);
		border-radius: var(--radius);
		padding: 1.5rem;
		box-shadow: var(--shadow);
		color: var(--color-text);
		transition: transform 0.15s, box-shadow 0.15s;
	}

	.feature-card:hover {
		transform: translateY(-2px);
		box-shadow: var(--shadow-md);
		text-decoration: none;
	}

	.feature-card h3 {
		color: var(--color-primary);
		margin-bottom: 0.5rem;
	}

	.feature-card p {
		color: var(--color-text-secondary);
		font-size: 0.9rem;
	}

	.categories {
		display: flex;
		flex-wrap: wrap;
		gap: 0.5rem;
	}

	.cat-tag {
		padding: 0.35rem 0.75rem;
		background: var(--color-bg);
		border-radius: 20px;
		font-size: 0.85rem;
		color: var(--color-text-secondary);
		border: 1px solid var(--color-border);
	}
</style>
