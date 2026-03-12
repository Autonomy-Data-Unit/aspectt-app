<script lang="ts">
	import { getTechSkillsBrowse, type TechBrowseItem } from '$lib/api/client';

	let items = $state<TechBrowseItem[]>([]);
	let total = $state(0);
	let loading = $state(true);
	let query = $state('');
	let debounceTimer: ReturnType<typeof setTimeout>;

	$effect(() => {
		load();
	});

	async function load() {
		loading = true;
		const data = await getTechSkillsBrowse(query, 200);
		items = data.technology_skills;
		total = data.total;
		loading = false;
	}

	function onInput() {
		clearTimeout(debounceTimer);
		debounceTimer = setTimeout(() => load(), 250);
	}
</script>

<svelte:head><title>Browse technology skills - ASPECTT</title></svelte:head>

<div class="container">
	<h1 class="page-title">Browse by technology</h1>
	<p class="page-desc">Software, programming languages and other technologies used across occupations. Select a technology to search for occupations that use it.</p>

	<div class="filter-row">
		<input class="search-input" type="text" placeholder="Filter technologies..." bind:value={query} oninput={onInput} />
	</div>

	{#if loading}
		<div class="loading"><div class="spinner"></div></div>
	{:else}
		<p class="result-count">{total} technologies{query ? ` matching "${query}"` : ''}</p>
		<div class="tech-grid">
			{#each items as item}
				<a href="/search/technology?q={encodeURIComponent(item.name)}" class="tech-card">
					<span class="tech-name">{item.name}</span>
					<span class="tech-count">{item.occupation_count} occupation{item.occupation_count !== 1 ? 's' : ''}</span>
				</a>
			{/each}
		</div>
	{/if}
</div>

<style>
	.filter-row { margin-bottom: 1.25rem; max-width: 400px; }

	.result-count { font-size: 0.85rem; color: var(--color-text-secondary); margin-bottom: 1rem; }

	.tech-grid {
		display: grid; grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)); gap: 0.75rem;
	}

	.tech-card {
		display: flex; flex-direction: column; gap: 0.25rem;
		padding: 0.875rem 1rem; background: var(--color-surface); border: 1px solid var(--color-border);
		border-radius: var(--radius); color: var(--color-text); transition: all var(--transition);
		box-shadow: var(--shadow-xs);
	}
	.tech-card:hover {
		border-color: var(--color-border-hover); box-shadow: var(--shadow); transform: translateY(-1px);
		text-decoration: none;
	}
	.tech-name { font-weight: 500; font-size: 0.875rem; }
	.tech-count { font-size: 0.75rem; color: var(--color-text-secondary); }
</style>
