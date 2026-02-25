<script lang="ts">
	import { searchOccupations, getStats, type Occupation, type Stats } from '$lib/api/client';
	import { goto } from '$app/navigation';

	let query = $state('');
	let results = $state<Occupation[]>([]);
	let total = $state(0);
	let stats = $state<Stats | null>(null);
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
		debounceTimer = setTimeout(async () => {
			const data = await searchOccupations(query, 12);
			results = data.occupations;
			total = data.total;
		}, 200);
	}

	function handleKeydown(e: KeyboardEvent) {
		if (e.key === 'Escape') { results = []; total = 0; }
	}

	function handleSubmit(e: Event) {
		e.preventDefault();
		if (query.trim()) goto(`/search?q=${encodeURIComponent(query.trim())}`);
	}
</script>

<div class="hero">
	<div class="container">
		<h1>ASPECTT</h1>
		<p class="tagline">UK occupational information system</p>
		<p class="desc">
			Skills, tasks, abilities, knowledge and technology data for {stats?.total_occupations ?? '...'} UK occupations, classified under SOC 2020.
		</p>

		<form class="search-box" onsubmit={handleSubmit}>
			<input
				class="search-input search-hero"
				type="text"
				placeholder="Search by title, alternate title or SOC code"
				bind:value={query}
				oninput={handleInput}
				onkeydown={handleKeydown}
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
						View all {total} results &rarr;
					</a>
				{/if}
			</div>
		{/if}
	</div>
</div>

<div class="container">
	<section class="section">
		<h2 class="section-heading">Browse occupations</h2>
		<div class="grid grid-4">
			<a href="/browse" class="nav-card">
				<h3>Major groups</h3>
				<p>The 9 SOC 2020 major groups and their occupations.</p>
			</a>
			<a href="/browse/job-zones" class="nav-card">
				<h3>Job zones</h3>
				<p>Occupations grouped by the preparation and education they typically require.</p>
			</a>
			<a href="/browse/interests" class="nav-card">
				<h3>Interests (RIASEC)</h3>
				<p>Occupations grouped by Holland interest codes.</p>
			</a>
			<a href="/browse/all" class="nav-card">
				<h3>All occupations</h3>
				<p>The full list of {stats?.total_occupations ?? '412'} occupations, with filters.</p>
			</a>
		</div>
	</section>

	<section class="section">
		<h2 class="section-heading">Search</h2>
		<div class="grid grid-4">
			<a href="/search/tasks" class="nav-card">
				<h3>Job duties</h3>
				<p>Search across {stats?.total_tasks ? stats.total_tasks.toLocaleString() : '...'} task statements.</p>
			</a>
			<a href="/search/technology" class="nav-card">
				<h3>Technology</h3>
				<p>Find occupations by the software, tools and technologies they use.</p>
			</a>
			<a href="/search/skills" class="nav-card">
				<h3>Skills</h3>
				<p>Occupations ranked by a given skill's importance.</p>
			</a>
			<a href="/compare" class="nav-card">
				<h3>Compare</h3>
				<p>Place two to four occupations side by side.</p>
			</a>
		</div>
	</section>

	<section class="section">
		<h2 class="section-heading">Browse by descriptor</h2>
		<div class="descriptor-grid">
			<a href="/browse/descriptors/skills" class="desc-link">Skills</a>
			<a href="/browse/descriptors/abilities" class="desc-link">Abilities</a>
			<a href="/browse/descriptors/knowledge" class="desc-link">Knowledge</a>
			<a href="/browse/descriptors/work_activities" class="desc-link">Work activities</a>
			<a href="/browse/descriptors/work_context" class="desc-link">Work context</a>
			<a href="/browse/descriptors/work_styles" class="desc-link">Work styles</a>
		</div>
	</section>

	<section class="section">
		<div class="grid grid-2">
			<a href="/crosswalk" class="nav-card">
				<h3>SOC crosswalk</h3>
				<p>The mapping between US O*NET SOC codes and UK SOC 2020.</p>
			</a>
			<a href="/api" class="nav-card">
				<h3>Public API</h3>
				<p>Access occupation data programmatically via the REST API.</p>
			</a>
		</div>
	</section>
</div>

<style>
	.hero {
		background: var(--color-primary);
		color: white;
		padding: 3.5rem 0 4rem;
		margin: -2.5rem 0 2.5rem;
		text-align: center;
		position: relative;
	}

	h1 {
		font-size: 2.25rem;
		letter-spacing: 0.12em;
		font-weight: 700;
		margin-bottom: 0.375rem;
	}

	.tagline {
		font-size: 1rem;
		opacity: 0.6;
		margin-bottom: 0.75rem;
		font-weight: 400;
		letter-spacing: 0.02em;
	}

	.desc {
		max-width: 520px;
		margin: 0 auto 1.75rem;
		opacity: 0.5;
		font-size: 0.875rem;
		line-height: 1.6;
	}

	.search-box {
		display: flex;
		gap: 0.5rem;
		max-width: 560px;
		margin: 0 auto;
		position: relative;
	}

	.search-hero {
		flex: 1;
		border: none;
		box-shadow: none;
		font-size: 0.9rem;
		padding: 0.7rem 1rem;
	}

	.search-btn {
		padding: 0.7rem 1.25rem;
		font-size: 0.875rem;
		background: var(--color-accent);
		border-color: var(--color-accent);
		color: var(--color-primary);
		font-weight: 600;
	}

	.search-btn:hover {
		background: var(--color-accent-light);
		border-color: var(--color-accent-light);
	}

	.results-dropdown {
		position: absolute;
		top: 100%;
		left: 50%;
		transform: translateX(-50%);
		width: 100%;
		max-width: 640px;
		background: white;
		border: 1px solid var(--color-border);
		border-radius: var(--radius-lg);
		box-shadow: var(--shadow-lg);
		z-index: 50;
		margin-top: 0.375rem;
		overflow: hidden;
	}

	.result-item {
		display: flex;
		gap: 0.75rem;
		padding: 0.5rem 1rem;
		color: var(--color-text);
		font-size: 0.875rem;
		white-space: nowrap;
	}

	.result-item:hover {
		background: var(--color-bg);
		text-decoration: none;
	}

	.result-code {
		font-family: 'SF Mono', SFMono-Regular, ui-monospace, monospace;
		font-weight: 600;
		color: var(--color-accent);
		flex: 0 0 50px;
		font-size: 0.8125rem;
	}

	.result-title {
		flex: 1;
		text-align: left;
		overflow: hidden;
		text-overflow: ellipsis;
	}

	.result-more {
		display: block;
		padding: 0.5rem 1rem;
		text-align: center;
		background: var(--color-bg);
		font-size: 0.8125rem;
		font-weight: 500;
		color: var(--color-text-secondary);
	}

	.result-more:hover {
		color: var(--color-text);
		text-decoration: none;
	}

	.section {
		margin-bottom: 2.25rem;
	}

	.section-heading {
		font-size: 0.8125rem;
		font-weight: 600;
		text-transform: uppercase;
		letter-spacing: 0.08em;
		color: var(--color-text-secondary);
		margin-bottom: 0.875rem;
	}

	.grid {
		display: grid;
		gap: 0.875rem;
	}

	.grid-4 {
		grid-template-columns: repeat(4, 1fr);
	}

	.grid-2 {
		grid-template-columns: repeat(2, 1fr);
	}

	.nav-card {
		background: var(--color-surface);
		border: 1px solid var(--color-border);
		border-radius: var(--radius-lg);
		padding: 1.25rem;
		color: var(--color-text);
		transition: border-color 0.15s;
	}

	.nav-card:hover {
		border-color: var(--color-accent);
		text-decoration: none;
	}

	.nav-card h3 {
		font-size: 0.9375rem;
		font-weight: 600;
		margin-bottom: 0.3rem;
		letter-spacing: -0.01em;
	}

	.nav-card p {
		color: var(--color-text-secondary);
		font-size: 0.8125rem;
		line-height: 1.5;
	}

	.descriptor-grid {
		display: grid;
		grid-template-columns: repeat(6, 1fr);
		gap: 0.5rem;
	}

	.desc-link {
		display: block;
		padding: 0.625rem 0.875rem;
		background: var(--color-surface);
		border: 1px solid var(--color-border);
		border-radius: var(--radius);
		color: var(--color-text);
		font-weight: 500;
		font-size: 0.8125rem;
		text-align: center;
		transition: border-color 0.15s;
	}

	.desc-link:hover {
		text-decoration: none;
		border-color: var(--color-accent);
		color: var(--color-accent);
	}

	@media (max-width: 900px) {
		.grid-4 {
			grid-template-columns: repeat(2, 1fr);
		}
		.descriptor-grid {
			grid-template-columns: repeat(3, 1fr);
		}
	}

	@media (max-width: 600px) {
		.grid-4, .grid-2 {
			grid-template-columns: 1fr;
		}
		.descriptor-grid {
			grid-template-columns: repeat(2, 1fr);
		}
		h1 {
			font-size: 1.75rem;
		}
	}
</style>
