<script lang="ts">
	import { searchTechSkills, type TechSearchResult } from '$lib/api/client';

	let query = $state('');
	let results = $state<TechSearchResult[]>([]);
	let matchingNames = $state<string[]>([]);
	let total = $state(0);
	let loading = $state(false);
	let searched = $state(false);

	async function doSearch() {
		if (!query.trim()) return;
		loading = true;
		searched = true;
		const data = await searchTechSkills(query, 100);
		results = data.results;
		matchingNames = data.matching_technology_names;
		total = data.total;
		loading = false;
	}

	function onKeydown(e: KeyboardEvent) {
		if (e.key === 'Enter') doSearch();
	}
</script>

<svelte:head><title>Technology search - ASPECTT</title></svelte:head>

<div class="container">
	<h1 class="page-title">Technology search</h1>
	<p class="page-desc">Find occupations that use specific software, tools or technologies.</p>

	<div class="card">
		<div class="search-row">
			<input class="search-input" type="text" placeholder="e.g. Python, Excel, SAP, AutoCAD..."
				bind:value={query} onkeydown={onKeydown} />
			<button class="btn btn-primary" onclick={doSearch}>Search</button>
		</div>
	</div>

	{#if loading}
		<div class="loading"><div class="spinner"></div></div>
	{:else if searched}
		<div class="card">
			{#if matchingNames.length > 0}
				<div class="matching-techs">
					<strong>Matching technologies:</strong>
					{#each matchingNames.slice(0, 15) as name}
						<span class="tech-tag">{name}</span>
					{/each}
					{#if matchingNames.length > 15}
						<span class="more">and {matchingNames.length - 15} more</span>
					{/if}
				</div>
			{/if}

			<h2>Occupations ({total})</h2>
			{#if results.length === 0}
				<p class="no-results">No occupations found using technologies matching "{query}"</p>
			{:else}
				<div class="results">
					{#each results as r}
						<a href="/occupation/{r.uk_soc_2020}" class="result-item">
							<div class="result-header">
								<span class="occ-code">{r.uk_soc_2020}</span>
								<span class="occ-title">{r.title}</span>
								<span class="match-count">{r.match_count} matches</span>
							</div>
							<div class="matching-list">
								{#each r.matching_technologies.slice(0, 8) as tech}
									<span class="match-tag">{tech}</span>
								{/each}
								{#if r.matching_technologies.length > 8}
									<span class="more">+{r.matching_technologies.length - 8}</span>
								{/if}
							</div>
						</a>
					{/each}
				</div>
			{/if}
		</div>
	{/if}
</div>

<style>
	.search-row { display: flex; gap: 0.625rem; }
	.search-row .search-input { flex: 1; }

	.matching-techs { display: flex; flex-wrap: wrap; gap: 0.4rem; align-items: center; margin-bottom: 1rem; padding-bottom: 1rem; border-bottom: 1px solid var(--color-border); }
	.tech-tag { padding: 0.2rem 0.5rem; background: var(--color-bg); border: 1px solid var(--color-border); border-radius: 12px; font-size: 0.75rem; }
	.more { font-size: 0.8rem; color: var(--color-text-secondary); }

	.results { display: flex; flex-direction: column; }
	.result-item { display: block; padding: 0.75rem 0; border-bottom: 1px solid var(--color-border); color: var(--color-text); }
	.result-item:last-child { border-bottom: none; }
	.result-item:hover { text-decoration: none; }
	.result-header { display: flex; gap: 0.5rem; align-items: center; margin-bottom: 0.35rem; }
	.occ-code { font-family: 'SF Mono', SFMono-Regular, ui-monospace, monospace; font-weight: 700; color: var(--color-accent); font-size: 0.8125rem; }
	.occ-title { flex: 1; font-weight: 500; }
	.match-count { font-size: 0.75rem; color: var(--color-text-secondary); background: var(--color-bg); padding: 0.15rem 0.5rem; border-radius: 12px; }
	.matching-list { display: flex; flex-wrap: wrap; gap: 0.3rem; }
	.match-tag { padding: 0.15rem 0.4rem; background: var(--color-accent-subtle); border-radius: 8px; font-size: 0.7rem; color: var(--color-accent); }
	.no-results { color: var(--color-text-secondary); text-align: center; padding: 2rem; }
</style>
