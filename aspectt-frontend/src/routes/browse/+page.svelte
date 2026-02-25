<script lang="ts">
	import { getMajorGroups, listOccupations, type MajorGroup, type Occupation } from '$lib/api/client';

	let majorGroups = $state<MajorGroup[]>([]);
	let selectedGroup = $state<number | null>(null);
	let occupations = $state<Occupation[]>([]);
	let loading = $state(true);
	let loadingOccs = $state(false);

	$effect(() => {
		getMajorGroups().then((data) => {
			majorGroups = data.major_groups;
			loading = false;
		});
	});

	async function selectGroup(code: number) {
		selectedGroup = code;
		loadingOccs = true;
		const data = await listOccupations({ majorGroup: code, limit: 500 });
		occupations = data.occupations;
		loadingOccs = false;
	}
</script>

<div class="container">
	<h1 class="page-title">Browse Occupations</h1>
	<p class="page-desc">Explore UK SOC 2020 occupations by major group.</p>

	{#if loading}
		<div class="loading"><div class="spinner"></div></div>
	{:else}
		<div class="groups">
			{#each majorGroups as group}
				<button
					class="group-card"
					class:active={selectedGroup === group.code}
					onclick={() => selectGroup(group.code)}
				>
					<span class="group-code">{group.code}</span>
					<span class="group-title">{group.title}</span>
					<span class="group-count">{group.occupation_count} occupations</span>
				</button>
			{/each}
		</div>

		{#if selectedGroup !== null}
			<div class="card">
				<h2>
					{majorGroups.find((g) => g.code === selectedGroup)?.title}
				</h2>

				{#if loadingOccs}
					<div class="loading"><div class="spinner"></div></div>
				{:else}
					<div class="occ-list">
						{#each occupations as occ}
							<a class="occ-item" href="/occupation/{occ.uk_soc_2020}">
								<span class="occ-code">{occ.uk_soc_2020}</span>
								{occ.title}
							</a>
						{/each}
					</div>
				{/if}
			</div>
		{/if}
	{/if}
</div>

<style>
	.page-title {
		font-size: 1.75rem;
		color: var(--color-primary);
		margin-bottom: 0.25rem;
	}

	.page-desc {
		color: var(--color-text-secondary);
		margin-bottom: 1.5rem;
	}

	.groups {
		display: grid;
		grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
		gap: 0.75rem;
		margin-bottom: 1.5rem;
	}

	.group-card {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		padding: 1rem;
		background: var(--color-surface);
		border: 2px solid var(--color-border);
		border-radius: var(--radius);
		cursor: pointer;
		transition: all 0.15s;
		text-align: left;
		font-size: 0.9rem;
	}

	.group-card:hover {
		border-color: var(--color-accent);
	}

	.group-card.active {
		border-color: var(--color-accent);
		background: #ebf4ff;
	}

	.group-code {
		font-size: 1.5rem;
		font-weight: 800;
		color: var(--color-accent);
		flex: 0 0 2.5rem;
		text-align: center;
	}

	.group-title {
		flex: 1;
		font-weight: 500;
	}

	.group-count {
		font-size: 0.8rem;
		color: var(--color-text-secondary);
	}

	.occ-list {
		display: flex;
		flex-direction: column;
	}

	.occ-item {
		display: flex;
		gap: 0.75rem;
		padding: 0.5rem 0;
		border-bottom: 1px solid var(--color-border);
		color: var(--color-text);
	}

	.occ-item:last-child {
		border-bottom: none;
	}

	.occ-item:hover {
		color: var(--color-accent);
		text-decoration: none;
	}

	.occ-code {
		font-family: monospace;
		font-weight: 600;
		color: var(--color-accent);
		flex: 0 0 50px;
	}
</style>
