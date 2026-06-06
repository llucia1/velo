{*
* 2007-2022 ETS-Soft
*
* NOTICE OF LICENSE
*
* This file is not open source! Each license that you purchased is only available for 1 wesite only.
* If you want to use this file on more websites (or projects), you need to purchase additional licenses. 
* You are not allowed to redistribute, resell, lease, license, sub-license or offer our resources to any third party.
* 
* DISCLAIMER
*
* Do not edit or add to this file if you wish to upgrade PrestaShop to newer
* versions in the future. If you wish to customize PrestaShop for your
* needs, please contact us for extra customization service at an affordable price
*
*  @author ETS-Soft <etssoft.jsc@gmail.com>
*  @copyright  2007-2022 ETS-Soft
*  @license    Valid for 1 website (or project) for each purchase of license
*  International Registered Trademark & Property of ETS-Soft
*}
<div class="header_content">
{block name='header_nav'}
  <nav class="header-nav">
    <div class="container">
        <div class="nav">
            <div class="left-nav">
              {hook h='displayNav1'}
              <div id="ybc_social_block" class="ybc_social_config">
            	<ul>
            		{if isset($tc_config.BLOCKSOCIAL_FACEBOOK) && $tc_config.BLOCKSOCIAL_FACEBOOK}
            			<li class="tc_facebook">
            				<a class="_blank" href="{$tc_config.BLOCKSOCIAL_FACEBOOK|escape:'html':'UTF-8'}">
            					<span><i class="fa fa-facebook"></i></span>
            				</a>
            			</li>
            		{/if}
            		{if isset($tc_config.BLOCKSOCIAL_TWITTER) && $tc_config.BLOCKSOCIAL_TWITTER}
            			<li class="tc_twitter">
            				<a class="_blank" href="{$tc_config.BLOCKSOCIAL_TWITTER|escape:'html':'UTF-8'}">
            					<span><i class="fa fa-twitter"></i></span>
            				</a>
            			</li>
            		{/if}
                    {if isset($tc_config.BLOCKSOCIAL_RSS) && $tc_config.BLOCKSOCIAL_RSS}
                    	<li class="tc_rss">
            				<a class="_blank" href="{$tc_config.BLOCKSOCIAL_RSS|escape:'html':'UTF-8'}">
            					<span><i class="fa fa-rss"></i></span>
            				</a>
            			</li>
                    {/if}
            		{if isset($tc_config.BLOCKSOCIAL_GOOGLE_PLUS) && $tc_config.BLOCKSOCIAL_GOOGLE_PLUS}
            			
                        <li class="tc_google-plus">
                    		<a class="_blank" href="{$tc_config.BLOCKSOCIAL_GOOGLE_PLUS|escape:'html':'UTF-8'}" rel="publisher">
                    			<span><i class="fa fa-google-plus"></i></span>
                    		</a>
                    	</li>
            		{/if}
                    {if isset($tc_config.BLOCKSOCIAL_INSTAGRAM) && $tc_config.BLOCKSOCIAL_INSTAGRAM}
                    	<li class="tc_instagram">
                    		<a class="_blank" href="{$tc_config.BLOCKSOCIAL_INSTAGRAM|escape:'html':'UTF-8'}">
                    			<span><i class="fa fa-instagram"></i></span>
                    		</a>
                    	</li>
                    {/if}
                    {if isset($tc_config.BLOCKSOCIAL_YOUTUBE) && $tc_config.BLOCKSOCIAL_YOUTUBE}
            			<li class="tc_youtube">
                    		<a class="_blank" href="{$tc_config.BLOCKSOCIAL_YOUTUBE|escape:'html':'UTF-8'}">
                    			<span><i class="fa fa-youtube-play"></i></span>
                    		</a>
                    	</li>
            		{/if}
                    {if isset($tc_config.BLOCKSOCIAL_PINTEREST) && $tc_config.BLOCKSOCIAL_PINTEREST}
                    	<li class="tc_pinterest">
                    		<a class="_blank" href="{$tc_config.BLOCKSOCIAL_PINTEREST|escape:'html':'UTF-8'}">
                    			<span><i class="fa fa-pinterest-p"></i></span>
                    		</a>
                    	</li>
                    {/if}
                    
                    {if isset($tc_config.BLOCKSOCIAL_VIMEO) && $tc_config.BLOCKSOCIAL_VIMEO}
                    	<li class="tc_vimeo">
                    		<a class="_blank" href="{$tc_config.BLOCKSOCIAL_VIMEO|escape:'html':'UTF-8'}">
                    			<span><i class="fa fa-vimeo-square"></i></span>
                    		</a>
                    	</li>
                    {/if}
                    
                    {if isset($tc_config.BLOCKSOCIAL_LINKEDIN) && $tc_config.BLOCKSOCIAL_LINKEDIN}
                    	<li class="tc_linkedin">
            				<a class="_blank" href="{$tc_config.BLOCKSOCIAL_LINKEDIN|escape:'html':'UTF-8'}">
            					<span><i class="fa fa-linkedin" ></i></span>
            				</a>
            			</li>
                    {/if}
            	</ul>
             </div>
            </div>
            <div class="right-nav">
                {hook h='displayNav2'}
            </div>
        </div>
    </div>
  </nav>
{/block}

{block name='header_top'}
  <div class="mobile_logo">
    <div class="" id="_mobile_logo">
      <a href="{$urls.base_url|escape:'html':'UTF-8'}">
        <img class="logo img-responsive" src="{if isset($tc_dev_mode) && $tc_dev_mode && isset($logo_url)&&$logo_url}{$logo_url|escape:'html':'UTF-8'}{else}{$shop.logo|escape:'html':'UTF-8'}{/if}" alt="{$shop.name|escape:'html':'UTF-8'}">
      </a>
    </div>
  </div>
  <div class="header-top">
    <div class="container">
       <div class="row">
        <div class="hidden-sm-down" id="_desktop_logo">
          <a href="{$urls.base_url|escape:'html':'UTF-8'}">
            <img class="logo img-responsive" src="{if isset($tc_dev_mode) && $tc_dev_mode && isset($logo_url)&&$logo_url}{$logo_url|escape:'html':'UTF-8'}{else}{$shop.logo|escape:'html':'UTF-8'}{/if}" alt="{$shop.name|escape:'html':'UTF-8'}">
          </a>
        </div>
        <div class="header_hook_top">
            {hook h='displayTop'}
            <span class="hidden-lg-up mobile closed" id="menu-icon">
              <i class="icon_menu"></i>
            </span>
        </div>
        {hook h='displayMegaMenu'}
      </div>
    </div>
  </div>
  {hook h='displayNavFullWidth'}
{/block}
</div>
{hook h='displayMLS'}
