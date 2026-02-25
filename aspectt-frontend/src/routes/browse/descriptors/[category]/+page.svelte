<script lang="ts">
	import { page } from '$app/state';
	import { getDescriptors, getDescriptorOccupations, type DescriptorElement, type DescriptorOccupation } from '$lib/api/client';

	let elements = $state<DescriptorElement[]>([]);
	let loading = $state(true);
	let category = $derived(page.params.category);
	let selectedElement = $state<string | null>(null);
	let elementOccupations = $state<DescriptorOccupation[]>([]);
	let elementTotal = $state(0);
	let loadingOccs = $state(false);

	const categoryLabels: Record<string, string> = {
		skills: 'Skills',
		abilities: 'Abilities',
		knowledge: 'Knowledge',
		work_activities: 'Work Activities',
		work_context: 'Work Context',
		work_styles: 'Work Styles',
	};

	const categoryDescriptions: Record<string, string> = {
		skills: 'Developed capacities that facilitate learning or the more rapid acquisition of knowledge.',
		abilities: 'Enduring attributes of the individual that influence performance.',
		knowledge: 'Organised sets of principles and facts applying in general domains.',
		work_activities: 'General types of job behaviours occurring on multiple jobs.',
		work_context: 'Physical and social factors that influence the nature of work.',
		work_styles: 'Personal characteristics that can affect how well someone performs a job.',
	};

	$effect(() => {
		loading = true;
		selectedElement = null;
		elementOccupations = [];
		getDescriptors(category, 100).then((data) => {
			elements = data.elements;
			loading = false;
		});
	});

	async function selectElement(name: string) {
		selectedElement = name;
		loadingOccs = true;
		const data = await getDescriptorOccupations(category, name);
		elementOccupations = data.occupations;
		elementTotal = data.total;
		loadingOccs = false;
	}
</script>

<svelte:head><title>{categoryLabels[category] ?? category} - ASPECTT</title></svelte:head>

<div class="container">
	<h1 class="page-title">Browse by {categoryLabels[category] ?? category}</h1>
	<p class="page-desc">{categoryDescriptions[category] ?? ''} Click an element to see which occupations score highest.</p>

	<div class="nav-pills">
		{#each Object.entries(categoryLabels) as [key, label]}
			<a href="/browse/descriptors/{key}" class="pill" class:active={key === category}>{label}</a>
		{/each}
	</div>

	{#if loading}
		<div class="loading"><div class="spinner"></div></div>
	{:else}
		<div class="layout">
			<div class="element-list card">
				<h2>{categoryLabels[category]} ({elements.length})</h2>
				{#each elements as el}
					<button
						class="element-item"
						class:active={selectedElement === el.element_name}
						onclick={() => selectElement(el.element_name)}
					>
						<span class="el-name">{el.element_name}</span>
						<span class="el-meta">{el.occupation_count} occs, avg {el.average_importance.toFixed(1)}</span>
					</button>
				{/each}
			</div>

			<div class="element-detail">
				{#if selectedElement}
					<div class="card">
						<h2>{selectedElement}</h2>
						<p class="detail-meta">
							{elementTotal} occupations use this {categoryLabels[category]?.toLowerCase() ?? 'element'}
						</p>
						{#if loadingOccs}
							<div class="loading"><div class="spinner"></div></div>
						{:else}
							<div class="occ-list">
								{#each elementOccupations as occ}
									<a href="/occupation/{occ.uk_soc_2020}" class="occ-row">
										<span class="occ-code">{occ.uk_soc_2020}</span>
										<span class="occ-title">{occ.title}</span>
										<div class="importance-bar-wrap">
											<div class="importance-bar" style="width: {(occ.importance / 5) * 100}%"></div>
										</div>
										<span class="importance-val">{occ.importance.toFixed(1)}</span>
									</a>
								{/each}
							</div>
						{/if}
					</div>
				{:else}
					<div class="card placeholder">
						<p>Select a {categoryLabels[category]?.toLowerCase() ?? 'descriptor'} from the list to see which occupations score highest.</p>
					</div>
				{/if}
			</div>
		</div>
	{/if}
</div>

<style>
	.page-title { font-size: 1.75rem; color: var(--color-primary); margin-bottom: 0.25rem; }
	.page-desc { color: var(--color-text-secondary); margin-bottom: 1rem; }

	.nav-pills { display: flex; gap: 0.5rem; flex-wrap: wrap; margin-bottom: 1.5rem; }
	.pill {
		padding: 0.35rem 0.75rem; border-radius: 20px; font-size: 0.85rem;
		background: var(--color-surface); border: 1px solid var(--color-border); color: var(--color-text);
	}
	.pill:hover { border-color: var(--color-accent); text-decoration: none; }
	.pill.active { background: var(--color-accent); color: white; border-color: var(--color-accent); }

	.layout { display: grid; grid-template-columns: 350px 1fr; gap: 1.5rem; }

	.element-list { max-height: calc(100vh - 250px); overflow-y: auto; }
	.element-list h2 { position: sticky; top: 0; background: var(--color-surface); z-index: 1; }

	.element-item {
		display: flex; justify-content: space-between; align-items: center;
		padding: 0.5rem 0.75rem; background: none; border: none; width: 100%;
		cursor: pointer; border-radius: 4px; text-align: left; font-size: 0.85rem;
	}
	.element-item:hover { background: var(--color-bg); }
	.element-item.active { background: #ebf4ff; color: var(--color-accent); font-weight: 600; }
	.el-meta { font-size: 0.75rem; color: var(--color-text-secondary); }

	.detail-meta { font-size: 0.9rem; color: var(--color-text-secondary); margin-bottom: 1rem; }

	.occ-list { display: flex; flex-direction: column; }
	.occ-row {
		display: flex; align-items: center; gap: 0.75rem; padding: 0.4rem 0;
		border-bottom: 1px solid var(--color-border); color: var(--color-text); font-size: 0.85rem;
	}
	.occ-row:last-child { border-bottom: none; }
	.occ-row:hover { color: var(--color-accent); text-decoration: none; }
	.occ-code { flex: 0 0 50px; font-family: monospace; font-weight: 600; color: var(--color-accent); }
	.occ-title { flex: 1; }
	.importance-bar-wrap { flex: 0 0 80px; height: 8px; background: var(--color-border); border-radius: 4px; overflow: hidden; }
	.importance-bar { height: 100%; background: var(--color-accent); border-radius: 4px; }
	.importance-val { flex: 0 0 30px; text-align: right; font-size: 0.8rem; color: var(--color-text-secondary); }

	.placeholder { text-align: center; padding: 3rem; color: var(--color-text-secondary); }

	@media (max-width: 768px) {
		.layout { grid-template-columns: 1fr; }
		.element-list { max-height: 300px; }
	}
</style>
