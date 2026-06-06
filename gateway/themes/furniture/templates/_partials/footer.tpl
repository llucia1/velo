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
<div class="footer-container">
  <div class="container">
        {hook h='ybcCustom1'}
        <div class="footer_top">
            {hook h='displayFooter'}
        </div> 
  </div>
  <div class="footer_after">
      <div class="container">
       <div class="row">
          <div class="ybc_coppyright col-xs-12 col-md-6">
             {if isset($tc_config.YBC_TC_COPYRIGHT_TEXT) && $tc_config.YBC_TC_COPYRIGHT_TEXT}
                {$tc_config.YBC_TC_COPYRIGHT_TEXT nofilter}
             {/if}
          </div>
          {if isset($tc_config.YBC_TC_PAYMENT_LOGO) && $tc_config.YBC_TC_PAYMENT_LOGO}
             <div class="payment_footer col-xs-12 col-md-6">
                <img src="{$tc_module_path|escape:'html':'UTF-8'}images/config/{$tc_config.YBC_TC_PAYMENT_LOGO|escape:'html':'UTF-8'}" alt="{l s='Payment methods'}" title="{l s='Payment methods'}" />
             </div>
          {/if}
        </div>
      </div>
  </div>
  <div class="footer_before">
      <div class="container">
          <div class="row">
            {hook h='displayFooterBefore'}
            {hook h='displayFooterAfter'}
            {*if isset($tc_config.YBC_FOOTER_LINK_CUSTOM) && $tc_config.YBC_FOOTER_LINK_CUSTOM}
                <div class="footer_link_bottom">
                    {$tc_config.YBC_FOOTER_LINK_CUSTOM nofilter}
                </div>
             {/if*}
          </div>
      </div>
  </div>
  <div class="scroll_top"><span>{l s='TOP' d='Shop.Theme.Actions'}</span></div>
</div>
