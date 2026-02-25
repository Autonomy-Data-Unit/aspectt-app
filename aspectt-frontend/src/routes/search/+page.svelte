<script lang="ts">
	import { page } from '$app/state';
	import { goto } from '$app/navigation';
	import { untrack } from 'svelte';
	import { searchOccupations, type Occupation } from '$lib/api/client';

	let query = $state(page.url.searchParams.get('q') || '');
	let results = $state<Occupation[]>([]);
	let total = $state(0);
	let loading = $state(false);
	let currentPage = $state(0);
	const pageSize = 50;

	$effect(() => {
		const q = page.url.searchParams.get('q');
		if (q) {
			query = q;
			untrack(() => doSearch());
		}
	});

	async function doSearch(offset = 0) {
		if (!query.trim()) return;
		loading = true;
		currentPage = offset;
		const data = await searchOccupations(query, pageSize, offset);
		results = data.occupations;
		total = data.total;
		loading = false;
	}

	function handleSubmit(e: Event) {
		e.preventDefault();
		goto(`/search?q=${encodeURIComponent(query.trim())}`, { replaceState: true });
		doSearch();
	}
</script>

<div class="container">
	<h1 class="page-title">Search occupations</h1>

	<form class="search-form" onsubmit={handleSubmit}>
		<input
			class="search-input"
			type="text"
			placeholder="Enter occupation title, keyword, or SOC code..."
			bind:value={query}
		/>
		<button class="btn btn-primary" type="submit">Search</button>
	</form>

	{#if loading}
		<div class="loading"><div class="spinner"></div></div>
	{:else if total > 0}
		<p class="result-count">{total} occupation{total !== 1 ? 's' : ''} found</p>
		<div class="results">
			{#each results as occ}
				<a class="result-row" href="/occupation/{occ.uk_soc_2020}">
					<span class="result-code">{occ.uk_soc_2020}</span>
					<span class="result-title">{occ.title}</span>
				</a>
			{/each}
		</div>

		{#if total > pageSize}
			<div class="pagination">
				{#if currentPage > 0}
					<button class="btn" onclick={() => doSearch(currentPage - pageSize)}>← Previous</button>
				{/if}
				<span class="page-info">
					Showing {currentPage + 1}–{Math.min(currentPage + pageSize, total)} of {total}
				</span>
				{#if currentPage + pageSize < total}
					<button class="btn" onclick={() => doSearch(currentPage + pageSize)}>Next →</button>
				{/if}
			</div>
		{/if}
	{:else if query.trim()}
		<p class="no-results">No occupations found matching "{query}"</p>
	{/if}
</div>

<style>
	.search-form {
		display: flex;
		gap: 0.625rem;
		margin-bottom: 1.75rem;
	}

	.search-form .search-input {
		flex: 1;
	}

	.result-count {
		color: var(--color-text-secondary);
		margin-bottom: 0.875rem;
		font-size: 0.875rem;
	}

	.results {
		background: var(--color-surface);
		border-radius: var(--radius-lg);
		border: 1px solid var(--color-border);
		overflow: hidden;
		box-shadow: var(--shadow-xs);
	}

	.result-row {
		display: flex;
		gap: 1rem;
		padding: 0.75rem 1.125rem;
		border-bottom: 1px solid var(--color-border);
		color: var(--color-text);
		transition: background var(--transition);
	}

	.result-row:last-child {
		border-bottom: none;
	}

	.result-row:hover {
		background: var(--color-bg);
		text-decoration: none;
	}

	.result-code {
		font-family: 'SF Mono', SFMono-Regular, ui-monospace, monospace;
		font-weight: 600;
		font-size: 0.8125rem;
		color: var(--color-accent);
		flex: 0 0 55px;
	}

	.result-title {
		flex: 1;
	}

	.pagination {
		display: flex;
		align-items: center;
		justify-content: center;
		gap: 1rem;
		margin-top: 1.75rem;
	}

	.page-info {
		color: var(--color-text-secondary);
		font-size: 0.875rem;
	}

	.no-results {
		text-align: center;
		color: var(--color-text-secondary);
		padding: 3rem;
		font-size: 0.9375rem;
	}
</style>
