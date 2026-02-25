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
				placeholder="Search occupations by title, alternate title, or SOC code..."
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
						View all {total} results &rarr;
					</a>
				{/if}
			</div>
		{/if}
	</div>
</div>

<div class="container">
	<h2 class="section-heading">Find Occupations</h2>
	<div class="features">
		<a href="/browse" class="feature-card">
			<div class="card-icon">&#x1f3e2;</div>
			<h3>Major Groups</h3>
			<p>Browse 9 SOC major groups covering all sectors of the UK economy.</p>
		</a>
		<a href="/browse/job-zones" class="feature-card">
			<div class="card-icon">&#x1f393;</div>
			<h3>Job Zones</h3>
			<p>Find occupations by education and preparation level required.</p>
		</a>
		<a href="/browse/interests" class="feature-card">
			<div class="card-icon">&#x2728;</div>
			<h3>Interests (RIASEC)</h3>
			<p>Explore occupations matching Holland interest codes.</p>
		</a>
		<a href="/browse/all" class="feature-card">
			<div class="card-icon">&#x1f4cb;</div>
			<h3>All Occupations</h3>
			<p>View and filter the complete list of {stats?.total_occupations ?? '412'} occupations.</p>
		</a>
	</div>

	<h2 class="section-heading">Advanced Search</h2>
	<div class="features">
		<a href="/search/tasks" class="feature-card">
			<div class="card-icon">&#x1f4dd;</div>
			<h3>Job Duties</h3>
			<p>Search across {stats?.total_tasks ? stats.total_tasks.toLocaleString() : '...'} task statements to find occupations by specific duties.</p>
		</a>
		<a href="/search/technology" class="feature-card">
			<div class="card-icon">&#x1f4bb;</div>
			<h3>Technology Skills</h3>
			<p>Find occupations that use specific software, tools, and technologies.</p>
		</a>
		<a href="/search/skills" class="feature-card">
			<div class="card-icon">&#x1f9e0;</div>
			<h3>Skills Search</h3>
			<p>Find occupations requiring specific skills, ranked by importance.</p>
		</a>
		<a href="/compare" class="feature-card">
			<div class="card-icon">&#x2696;</div>
			<h3>Compare</h3>
			<p>Compare 2-4 occupations side by side across all data categories.</p>
		</a>
	</div>

	<h2 class="section-heading">Browse by Descriptor</h2>
	<div class="descriptor-grid">
		<a href="/browse/descriptors/skills" class="desc-card">Skills<span class="desc-arrow">&rarr;</span></a>
		<a href="/browse/descriptors/abilities" class="desc-card">Abilities<span class="desc-arrow">&rarr;</span></a>
		<a href="/browse/descriptors/knowledge" class="desc-card">Knowledge<span class="desc-arrow">&rarr;</span></a>
		<a href="/browse/descriptors/work_activities" class="desc-card">Work Activities<span class="desc-arrow">&rarr;</span></a>
		<a href="/browse/descriptors/work_context" class="desc-card">Work Context<span class="desc-arrow">&rarr;</span></a>
		<a href="/browse/descriptors/work_styles" class="desc-card">Work Styles<span class="desc-arrow">&rarr;</span></a>
	</div>

	<div class="bottom-row">
		<a href="/crosswalk" class="feature-card">
			<div class="card-icon">&#x1f517;</div>
			<h3>SOC Crosswalk</h3>
			<p>Explore the mapping between US O*NET SOC codes and UK SOC 2020.</p>
		</a>
		<a href="/api" class="feature-card">
			<div class="card-icon">&#x2699;</div>
			<h3>Public API</h3>
			<p>Access all occupation data programmatically via our REST API.</p>
		</a>
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

	h1 { font-size: 3rem; letter-spacing: 6px; font-weight: 800; margin-bottom: 0.25rem; }
	.subtitle { font-size: 1.2rem; opacity: 0.85; margin-bottom: 0.75rem; }
	.desc { max-width: 600px; margin: 0 auto 1.5rem; opacity: 0.75; font-size: 0.95rem; }

	.search-box { display: flex; gap: 0.5rem; max-width: 600px; margin: 0 auto; position: relative; }
	.search-hero { flex: 1; border: none; box-shadow: var(--shadow-md); }
	.search-btn { padding: 0.75rem 1.5rem; font-size: 1rem; }

	.results-dropdown {
		position: absolute; top: 100%; left: 50%; transform: translateX(-50%);
		width: 100%; max-width: 600px; background: white;
		border-radius: var(--radius); box-shadow: var(--shadow-md);
		z-index: 50; margin-top: 0.25rem; overflow: hidden;
	}
	.result-item { display: flex; gap: 0.75rem; padding: 0.6rem 1rem; color: var(--color-text); }
	.result-item:hover { background: var(--color-bg); text-decoration: none; }
	.result-code { font-family: monospace; font-weight: 600; color: var(--color-accent); flex: 0 0 50px; }
	.result-title { flex: 1; text-align: left; }
	.result-more { display: block; padding: 0.5rem 1rem; text-align: center; background: var(--color-bg); font-size: 0.875rem; font-weight: 500; }

	.section-heading { font-size: 1.25rem; color: var(--color-primary); margin-bottom: 1rem; margin-top: 0.5rem; }

	.features { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 1rem; margin-bottom: 2rem; }

	.feature-card {
		background: var(--color-surface); border-radius: var(--radius); padding: 1.25rem;
		box-shadow: var(--shadow); color: var(--color-text); transition: transform 0.15s, box-shadow 0.15s;
		border: 1px solid transparent;
	}
	.feature-card:hover { transform: translateY(-2px); box-shadow: var(--shadow-md); text-decoration: none; border-color: var(--color-accent-light); }
	.feature-card h3 { color: var(--color-primary); margin-bottom: 0.35rem; font-size: 1rem; }
	.feature-card p { color: var(--color-text-secondary); font-size: 0.85rem; line-height: 1.5; }
	.card-icon { font-size: 1.5rem; margin-bottom: 0.5rem; }

	.descriptor-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(160px, 1fr)); gap: 0.5rem; margin-bottom: 2rem; }
	.desc-card {
		display: flex; justify-content: space-between; align-items: center;
		padding: 0.75rem 1rem; background: var(--color-surface); border-radius: var(--radius);
		box-shadow: var(--shadow); color: var(--color-primary); font-weight: 600; font-size: 0.9rem;
		border: 1px solid transparent;
	}
	.desc-card:hover { text-decoration: none; border-color: var(--color-accent); color: var(--color-accent); }
	.desc-arrow { color: var(--color-text-secondary); }

	.bottom-row { display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 1rem; margin-bottom: 2rem; }
</style>
