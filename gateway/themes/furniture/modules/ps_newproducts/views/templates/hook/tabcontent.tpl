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
<div id="new_products" class="featured-products clearfix home-block-section col-xs-12 col-sm-12">
  <div class="products product_list">
    {assign var='inp' value=0}
    {foreach from=$products item="product"}
        {if $inp%2 == 0 && count($products) > 4}
            <div class="group_item_products">
        {/if}
        {assign var='inp' value=$inp+1}
            {include file="catalog/_partials/miniatures/product.tpl" product=$product}
        {if $inp%2 == 0 && count($products) > 4}
            </div>
        {/if}
    {/foreach}
    {if $inp%2 != 0 && count($products) > 4}
            </div>
    {/if}
  </div>
</div>
