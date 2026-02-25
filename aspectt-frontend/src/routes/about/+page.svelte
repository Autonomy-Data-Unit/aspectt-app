<svelte:head><title>About - ASPECTT</title></svelte:head>

<div class="container">
	<h1 class="page-title">About ASPECTT</h1>

	<div class="card">
		<h2>What is ASPECTT?</h2>
		<p>
			ASPECTT (A System for Predicting and Evaluating Competencies, Tasks and Technologies)
			is a multidimensional occupational database for the UK. It provides information on the
			skills, tasks, abilities, knowledge, technologies and work characteristics associated
			with 412 UK occupations, classified under the SOC 2020 system.
		</p>
		<p>
			The UK has no direct equivalent of the US O*NET system, which gives detailed
			occupational data to researchers, policymakers, careers advisers and employers. ASPECTT
			fills that gap by adapting O*NET data for a UK context using a series of standard
			occupation code crosswalks.
		</p>
	</div>

	<div class="card">
		<h2>Methodology</h2>
		<p>
			ASPECTT maps US O*NET occupations to UK SOC 2020 codes through a chain of crosswalks:
		</p>
		<div class="crosswalk-chain">
			<span class="chain-step">US O*NET SOC</span>
			<span class="chain-arrow">&rarr;</span>
			<span class="chain-step">US SOC 2018</span>
			<span class="chain-arrow">&rarr;</span>
			<span class="chain-step">US SOC 2010</span>
			<span class="chain-arrow">&rarr;</span>
			<span class="chain-step">ISCO-08</span>
			<span class="chain-arrow">&rarr;</span>
			<span class="chain-step">UK SOC 2020</span>
		</div>
		<p>
			Where a UK occupation maps to more than one US O*NET occupation, the data is combined
			using uniform weights. Each UK occupation therefore represents a weighted average of its
			contributing O*NET sources. You can inspect these mappings and weights on the
			<a href="/crosswalk">crosswalk page</a> or in the 'Sources' tab of any occupation.
		</p>
		<p>
			The underlying O*NET data comes from version 30.2 of the O*NET database. The
			ISCO-08 to SOC crosswalk is provided by the US Bureau of Labor Statistics, and
			the UK SOC 2020 coding index is published by the Office for National Statistics.
		</p>
	</div>

	<div class="card">
		<h2>Data categories</h2>
		<p>Each occupation in ASPECTT includes information across these categories:</p>
		<ul class="data-list">
			<li><strong>Tasks</strong> &ndash; specific work activities carried out in the occupation</li>
			<li><strong>Skills</strong> &ndash; developed capacities that facilitate learning or performance</li>
			<li><strong>Abilities</strong> &ndash; enduring attributes that influence performance</li>
			<li><strong>Knowledge</strong> &ndash; organised sets of principles and facts</li>
			<li><strong>Technology skills</strong> &ndash; software, tools and technologies used</li>
			<li><strong>Work activities</strong> &ndash; general types of job behaviour</li>
			<li><strong>Work context</strong> &ndash; physical and social conditions of work</li>
			<li><strong>Work styles</strong> &ndash; personal characteristics relevant to performance</li>
			<li><strong>Interests</strong> &ndash; Holland (RIASEC) interest profiles</li>
			<li><strong>Work values</strong> &ndash; what workers in the occupation tend to value</li>
			<li><strong>Education</strong> &ndash; typical preparation level required</li>
		</ul>
	</div>

	<div class="card">
		<h2>Who built this</h2>
		<p>
			ASPECTT is produced by the <a href="https://autonomy.work/adu/" target="_blank" rel="noopener">Autonomy Data Unit</a>,
			the research and analytics division of the
			<a href="https://autonomy.work/" target="_blank" rel="noopener">Autonomy Institute</a>.
			Autonomy is an independent research organisation that creates data-driven tools and
			policy to strengthen democracy and build the future economy. Its work spans labour
			markets, public services and digital infrastructure.
		</p>
		<p>
			The Data Unit combines datasets, builds research tools and develops data visualisations
			to support policy research. ASPECTT is one of its long-running projects, giving UK
			researchers and policymakers access to the kind of granular occupational data that
			O*NET provides in the US.
		</p>
	</div>

	<div class="card">
		<h2>Further reading</h2>
		<ul class="link-list">
			<li><a href="https://autonomy.work/wp-content/uploads/2022/01/Aspectt-occupational-tool.pdf" target="_blank" rel="noopener">ASPECTT methodology paper (PDF)</a></li>
			<li><a href="https://autonomy.work/adu/" target="_blank" rel="noopener">Autonomy Data Unit</a></li>
			<li><a href="https://autonomy.work/" target="_blank" rel="noopener">Autonomy Institute</a></li>
			<li><a href="/api">ASPECTT public API</a></li>
		</ul>
	</div>
</div>

<style>
	.page-title { font-size: 1.75rem; color: var(--color-primary); margin-bottom: 1.5rem; }

	.card p { font-size: 0.95rem; line-height: 1.7; color: var(--color-text); margin-bottom: 0.75rem; }
	.card p:last-child { margin-bottom: 0; }

	.crosswalk-chain {
		display: flex; align-items: center; gap: 0.5rem; flex-wrap: wrap;
		padding: 1rem; background: var(--color-bg); border-radius: var(--radius);
		margin: 0.75rem 0;
	}
	.chain-step {
		padding: 0.35rem 0.75rem; background: var(--color-surface);
		border: 1px solid var(--color-border); border-radius: var(--radius);
		font-size: 0.85rem; font-weight: 600; white-space: nowrap;
	}
	.chain-arrow { color: var(--color-text-secondary); font-size: 1rem; }

	.data-list { padding-left: 1.25rem; margin-top: 0.5rem; }
	.data-list li { font-size: 0.9rem; line-height: 1.6; margin-bottom: 0.25rem; }

	.link-list { padding-left: 1.25rem; }
	.link-list li { font-size: 0.9rem; line-height: 1.8; }
</style>
