import {describe, it, expect, afterEach, vi, beforeEach} from "vitest";
import { mount } from '@vue/test-utils'
import users from './fixtures/sample_users'
import AdminEditUserDetails from "../AdminEditUserDetails.vue";
import agencies from './fixtures/sample_agency_response'
import {defineComponent} from "vue";

describe('AdminEditUserDetails', () => {
    beforeEach(() => {
        vi.spyOn(global, 'fetch').mockImplementation(() => {
            return Promise.resolve({ok: true, status:200, json: () => Promise.resolve(agencies) })
        })
    })

    afterEach(() => {
        vi.restoreAllMocks()
    })
    
    it('displays edit fields', async ()=>{
        const props = {userToEdit: users[0]}
        const wrapper = mount(AdminEditUserDetails, {props})
        const name = wrapper.find('input[id="name"]')
        const email = wrapper.find('input[id="input-email"]')
        const agency = wrapper.find('input[id="agency"]')
        const bureau = wrapper.find('input[id="bureau"]')

        expect(name.element.value).toBe('Hugh Steeply')
        expect(email.element.value).toBe('helen.steeply@ous.gov')
        expect(agency.element.value).toBe('Office of Unspecified Services')
        expect(bureau.element.value).toBe('Secret Service')
        expect(name.element.disabled).toBe(true)
    })

})